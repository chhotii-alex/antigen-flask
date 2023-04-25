import os
import random
from sqlalchemy import text
from flask import g

import numpy as np
import statsmodels.api as sm

import colors
import stats

salt = os.environ['JITTER_SALT']

def getJitter(query):
    seed = query + salt
    if 'random' not in g:
        g.random = random.Random()
    g.random.seed(seed)
    jitter = round(g.random.uniform(-3.5, 3.5))
    return jitter

def kernel_density(data, start=0.0, stop=11.0):
    data = np.asarray(data)[:, np.newaxis]
    numpoints = round((stop-start)/0.02)+1
    X = np.linspace(start, stop, numpoints)
    kde = sm.nonparametric.KDEUnivariate(data)
    kde.fit(kernel="gau", bw=0.25)
    density = kde.evaluate(X)
    density[0] = 0
    density[-1] = 0
    r = np.asarray([X, density]).transpose()
    return r

def andWhere(queryParts, cond):
    baseQuery = queryParts["base"]
    whereClause = queryParts["where"]
    whereClause = "%s AND %s " % (whereClause, cond)
    return {
        "base" : baseQuery,
        "where" : whereClause
    }

class PatientSetDescription:
    def __init__(self, baseObj=None, noun=None, adjective=None, modifier=None) :
        if baseObj is not None:
            self.noun = baseObj.noun
            self.adjectives = baseObj.getAdjectives()[:]
            self.modifiers = baseObj.modifiers[:]
        else:
            self.noun = "patients"
            self.adjectives = []
            self.modifiers = []
        
        if noun is not None:
            self.setNoun(noun)
        
        if adjective is not None:
            self.addAdjective(adjective)
        
        if modifier is not None:
            self.addModifier(modifier)
        
    def __str__(self):
        adj = " ".join(self.adjectives)
        mod = " ".join(self.modifiers)
        return "%s %s %s" % (adj, self.noun, mod)
    
    def addModifier(self, s):
        self.modifiers.append(s)
    
    def setNoun(self, s):
        if self.noun == "patients":
            self.noun = s
        else:
            self.noun = "%s, %s" % (self.noun, s)
    
    def addAdjective(self, s):
        self.adjectives.append(s)
    
    def getAdjectives(self):
        return self.adjectives

class QuerySet:
    def __init__(self, limitHit=False):
        self.queries = {}
        self.descriptions = {}
        self.sizeLimit = 32
        self.count = 0
        self.limitHit = limitHit

    def addQuery(self, description, query):
        if (self.isAtMaxSize()):
           self.limitHit = True
           return
        
        self.queries[str(description)] = query
        self.descriptions[str(description)] = description
        self.count += 1
    
    def getLabels(self):
        return self.queries.keys()
    
    def getCount(self):
       return self.count
    
    def isAtMaxSize(self):
       return (self.count >= self.sizeLimit)
    
def makeNewQueries(queries, updaterList):
    newQueries = QuerySet()
    for label in queries.getLabels():
        queryParts = queries.queries[label]
        oldSet = queries.descriptions[label]
        for updater in updaterList:
            newSet = PatientSetDescription(oldSet, updater.noun,
                       updater.adjective, updater.modifier)
            newQueryParts = andWhere(queryParts, updater.whereClause)
            newQueries.addQuery(newSet, newQueryParts)
    return newQueries

def compareArrays(arr1, arr2):
    if (len(arr1) < 1 or len(arr2) < 1):
        return None    
    p = stats.compare(arr1, arr2)
    return p
    # TODO: Why was I trimming the number of digits HERE? i.e.:
    #return Number.parseFloat(p.toPrecision(3))

def makeBaseQuery():
    return """SELECT viral_load_log viralloadlog
                     FROM DeidentResults """

def makeBaseWhereClause():
    whereClause = """ WHERE viral_load_log IS NOT NULL """
    return whereClause

# For info about variableObj, see werkzeug MultiDict
def splitQueries(queries, splits, variableObj):
    variableCount = 0
    splitVariableCount = 0
    fetchedAllGroups = False
    splitDescription = None
    for variable in variableObj.keys():
        lookup = variable.strip('[]')
        if lookup in splits:
            values = variableObj.getlist(variable)
            split = splits[lookup]
            groupsToFetch = [s for s in split.splits if s.value in values]
            variableCount += 1
            if len(groupsToFetch) > 1:
                splitVariableCount += 1
            
            if (splitVariableCount > 5):
               return [ QuerySet(True), None]
            
            if (len(groupsToFetch) == len(split.splits)) :
                fetchedAllGroups = True
                splitDescription = "Across %s" % split.variableDisplayName
        
            queries = makeNewQueries(queries, groupsToFetch)
          
    if (variableCount != 1 or not fetchedAllGroups) :
        splitDescription = None
    
    return [queries, splitDescription]
    
def runQuery(db, label, queryParts):
    baseQuery = queryParts["base"]
    whereClause = queryParts["where"]
    query = "%s %s" % (baseQuery, whereClause)
    query = query.strip()
    jitter = getJitter(query)
    rows = db.session.execute(text(query)).fetchall()
    if len(rows) < 4:
        return None
    if len(rows) + jitter < 4:
       return None

    rawData = [r.viralloadlog for r in rows]

    mean_val = np.power(10, np.mean(rawData))
    pop = {
               "label" : label,
               "mean" : mean_val,
               "count" : len(rawData),
               "comparisons" : []}
    if pop['count'] >= 60:
        density = kernel_density(rawData)        
        densityBinWidth = density[2][0] - density[1][0]
        halfBin = densityBinWidth/2
        total = len(rawData)
        pop["data"] = [
            {"viralLoadLog": density[i][0],
            "viralLoadLogMin": density[i][0] - halfBin,
            "viralLoadLogMax": density[i][0] + halfBin,
             "count": density[i][1]*total*2}
            for i
            in range(density.shape[0]) ]
    
    return {"rawData": rawData, "pop": pop}

def datafetch(db, splits, variables):
    tooManyQueries = False

    queries = QuerySet()
    queries.addQuery(PatientSetDescription(),
                     {"base":makeBaseQuery(),
                      "where":makeBaseWhereClause()})
    queries, splitDescription = splitQueries(queries,
                                             splits,
                                             variables)
    results = []
    numberOfQueriesAttempted = 0
    for label in queries.getLabels():
        if len(results) >= 8 or numberOfQueriesAttempted >= 32:
            tooManyQueries = True
            break
        result = runQuery(db, label, queries.queries[label])
        numberOfQueriesAttempted += 1
        if result:
            result['pop']['rawData'] = result['rawData']
            results.append(result['pop'])

    for pop in results:
        pop["catagories"] = {"count":"Count"}
        pop["median"] = np.median(pop["rawData"])

    results.sort(key=lambda pop:pop["median"])

    for i in range(len(results)):
        for j in range(i):
            pvalue = compareArrays(results[j]['rawData'],
                                   results[i]['rawData'])
            results[i]['comparisons'].append(pvalue)

    colorIndex = 0
    for pop in results:
        if 'data' in pop:
            pop['shouldPlot'] = True
            pop['colors'] = colors.getColorSchema(colorIndex)
            colorIndex += 1
        else:
            pop['shouldPlot'] = False
            pop['colors'] = colors.getPlainColors()
        del pop['median']
        del pop['rawData']

    return {"populations":results,
            "tooManyQueries":tooManyQueries,
            "tooManyVariables":queries.limitHit,
            "splitDescription":splitDescription, }
