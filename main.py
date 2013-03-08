import os
from flask import Flask
app = Flask(__name__)
app.debug = False

HOME = os.environ.get("HOME", "")
if HOME:
    HOME = HOME + "/"

@app.route("/")
def hello():
    try:
        return open(HOME + "blag/static/home.html", "r").read()
    except Exception, e:
        return str(e)

if __name__ == "__main__":
    app.run()
