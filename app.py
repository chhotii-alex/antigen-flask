from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.middleware.profiler import ProfilerMiddleware

import sys
import os
import json

import config
from stats import compare
import variables
import queries

db = SQLAlchemy()

app = Flask(__name__,
            static_url_path='',
            static_folder='static')
if 'FLASK_PROFILING' in os.environ:
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir="/Users/work/antigen-flask/profile_dir")
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = config.url
db.init_app(app)

print("Launching...")

with app.app_context():
    cachedVars, gSplits = variables.fetchVarsFromDB(app, db)

@app.route("/hello")
def hello_world():
    return """<h1>Hello, Web!!! </h1>this is the new implementation"""

@app.route("/api/assays")
def assays():
    data = {
        "items":[
            {"id":"binax",
             "displayName":"BinaxNOW&trade; COVID-19 Ag Card",
             "coef":1.1843183,
             "intercept":-5.37500995},
            {"id":"ginko",
             "displayName":"CareStart COVID-19 Antigen Home Test",
             "coef":1.14230231,
             "intercept":-5.70535991}
        ]
    }
    for item in data["items"]:
        item['ld50'] = -(item['intercept']/item['coef'])
    return data

@app.route("/api/variables")
def variables():
    data = {
        "items" : cachedVars,
        "version" : 1,
        }
    return data

@app.route("/api/data/viralloads")
def datafetch():
    return queries.datafetch(db, gSplits, request.args)
