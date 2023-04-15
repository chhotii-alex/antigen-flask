from sqlalchemy import text

class PatientSplit:
    def __init__(self, variable, variableDisplayName):
        self.variable = variable
        self.variableDisplayName = variableDisplayName
        self.splits = []

    def addSplit(self, splitSpecifier):
        self.splits.append(splitSpecifier)

class PatientSplitSpecifier:
    def __init__(self, row, splits):
        variable = row['variable']
        if variable in splits:
            split = splits[variable]
        else:
            variableDisplayName = row['variabledisplayname']
            split = PatientSplit(variable, variableDisplayName)
            splits[variable] = split
        split.addSplit(self)
        self.value = row['value']
        self.valueDisplayName = row['valuedisplayname']
        self.noun = row['noun']
        self.modifier = row['modifier']
        self.adjective = row['adjective']
        self.whereClause = row['whereclause']
        self._checked = row['initiallychecked']

def getVariableSplits(db, splits):
    query = """SELECT variable, variableDisplayName,
                        value, valueDisplayName, noun, adjective,
                        modifier, whereClause,
                      initiallyChecked
                    FROM UIVars ORDER BY sort"""
    r = db.session.execute(text(query))
    for row in r:
        PatientSplitSpecifier(row._mapping, splits)
    
def getTreatmentSplits(db, splits):
    query = "SELECT tag, description from TreatmentRef order by tag"
    r = db.session.execute(text(query))
    for row in r:
        tag = row.tag
        description = row.description
        d = {
                "variable": tag,
                "variabledisplayname": description.title(),
                "value": "true_%s" % tag,
                "valuedisplayname": "Received %s" % description.lower(),
                "noun": None,
                "modifier": "getting %s" % description.lower(),
                "adjective": None,
                "whereclause": tag.lower(),
                "initiallychecked": False}
        PatientSplitSpecifier(d, splits)
        d["value"] = "false_%s" % tag
        d["valuedisplayname"] = "Did not receive %s" % description.lower()
        d["modifier"] = "not getting %s" % description.lower()
        d["whereclause"] = "not %s" % tag.lower()
        PatientSplitSpecifier(d, splits)

def splitSpecifierForComorbidity(splits, tag, tags, group_description, flag):
    flagString = "false_"
    valueStringPrefix = "No reported"
    modifierPrefix = "with no"
    if (flag):
        flagString = "true_"
        valueStringPrefix = "Known"
        modifierPrefix = "with"
    if (flag):
        whereClause = "(" + " OR ".join(tags) + ")"
    else:
        not_tags = [" NOT %s " % tag for tag in tags]
        whereClause = "(" + " AND ".join(not_tags) + ")"
    d = {
        "variable": tag,
        "variabledisplayname": group_description.title(),
        "value": flagString + tag,
        "valuedisplayname": "%s %s" % (valueStringPrefix,
                                       group_description.lower()),
        "noun": None,
        "modifier": "%s %s" % (modifierPrefix,
                               group_description.lower()),
        "adjective": None,
        "whereclause": whereClause,
        "initiallychecked": False,
    }
    PatientSplitSpecifier(d, splits)

def getComorbiditySplits(db, splits):
    def do_splits():
        splitSpecifierForComorbidity(splits, prev_group, tags,
                group_description, True)
        splitSpecifierForComorbidity(splits, prev_group, tags,
            group_description, False)
   
    query = """SELECT g.tag group_tag, g.description group_name,
                   r.tag, r.description,
                   r.on_by_default
            from ComorbidityGroup g,
                         ComorbidityRef r
            WHERE g.tag = r.grouping
            order by g.sort_key, r.sort_key"""
    r = db.session.execute(text(query))
    prev_group = None
    group_description = None
    for row in r:
        group_tag = row.group_tag
        if (group_tag != prev_group):
            if prev_group is not None:
                do_splits()    
            tags = []
        tags.append(row.tag)
        group_description = row.group_name
        prev_group = group_tag
    do_splits()
   
def fetchVarsFromDB(app, db):
    with app.app_context():
        splits = {}
        getVariableSplits(db, splits)
        getTreatmentSplits(db, splits)
        getComorbiditySplits(db, splits)
        items = []
        for variable in splits.keys():
            split = splits[variable]
            divisions = []
            for spec in split.splits:
                divisions.append(
                    {"value": spec.value,
                     "valueDisplayName":spec.valueDisplayName,
                     "_checked":spec._checked,
                       })
            items.append(
                {"id": split.variable,
                 "displayName" : split.variableDisplayName,
                 "slits":divisions
                   })
        return (items, splits)
