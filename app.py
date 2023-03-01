from flask import Flask, send_from_directory

app = Flask(__name__,
            static_url_path='',
            static_folder='static')

@app.route("/hellow")
def hello_world():
    return "<h1>Hello, Web!!!</h1>"

@app.route("/")
def main():
    return send_from_directory('static', 'index.html')

@app.route("/sample")
def hello_content():
    return "<h1>HERE</h1>is my page."

@app.route("/assays")
def assays():
    data = {
        "items":[
            {"id":"binax","displayName":"BinaxNOW&trade; COVID-19 Ag Card","coef":1.1843183,"intercept":-5.37500995},
            {"id":"ginko","displayName":"CareStart COVID-19 Antigen Home Test","coef":1.14230231,"intercept":-5.70535991}
        ]
    }
    return data

