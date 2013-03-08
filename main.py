from flask import Flask
app = Flask(__name__)
app.debug = False

@app.route("/")
def home():
    with open("static/home.html") as fp:
        return fp.read()


@app.route("/test")
def test():
    with open("static/test.html") as fp:
        return fp.read()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
