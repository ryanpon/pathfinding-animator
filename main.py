import os, sys
from flask import Flask, make_response
app = Flask(__name__)
app.debug = False

HOME = os.environ.get("HOME", "")
if HOME:
    HOME = HOME + "/"

if "test" in sys.argv: 
    app.debug = True
    HOME += "Dropbox/"

@app.route("/")
def home():
    return open(HOME + "blag/static/index.html", "r").read()

@app.route("/static/resume.pdf")
def get_resume():
    response = make_response(open(HOME + "blag/static/resume.pdf", "r").read())
    response.headers["Content-Type"] = "application/pdf"
    return response

@app.route("/static/seq.j")
def test_seq():
    return open(HOME + "blag/routing/seq.j", "r").read()

@app.route("/test")
def test():
    return open(HOME + "blag/static/gmaps.html", "r").read()

if __name__ == "__main__":
    app.run()
