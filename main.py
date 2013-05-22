import os 
import sys
from flask import Flask, make_response, request
import json

if "test" in sys.argv:
    app.debug = True
    HOME = ""
    sys.path.append("./routing/")
else:
    HOME = "/home/ubuntu/blag/"
    sys.path.append(HOME + "routing/")
from AStar import PathfindingAnimator

app = Flask(__name__)
app.debug = True

ANIMATOR = None


def split_comma_ll(ll_string):
    s = ll_string.split(',')
    return float(s[0]), float(s[1])

def init_animator():
    global ANIMATOR
    with open(HOME + 'routing/sf.j', 'r') as fp:
        graph = json.loads(fp.read())
    with open(HOME + 'routing/sf_coords.j', 'r') as fp:
        graph_coords = json.loads(fp.read())
    ANIMATOR = PathfindingAnimator(graph, graph_coords)

@app.route("/")
def home():
    return open(HOME + "static/index.html", "r").read()

@app.route("/static/resume.pdf")
def get_resume():
    response = make_response(open(HOME + "static/resume.pdf", "r").read())
    response.headers["Content-Type"] = "application/pdf"
    return response

@app.route("/animation")
def search_animation():
    search_type = request.args.get("type")
    source = split_comma_ll(request.args.get("source"))
    dest = split_comma_ll(request.args.get("dest"))
    print search_type, source, dest
    if search_type == "dijkstra":
        seq, coords, path = ANIMATOR.dijkstra_animation(source, dest)
    elif search_type == "astar":
        seq, coords, path = ANIMATOR.astar_animation(source, dest)
    elif search_type == "alt":
        seq, coords, path = ANIMATOR.alt_animation(source, dest)
    response = {
        "sequence" : seq,
        "coords" : coords,
        "path" : path
    }
    return json.dumps(response)

@app.route("/test")
def test():
    return open(HOME + "static/gmaps.html", "r").read()

if __name__ == "__main__":
    init_animator()
    app.run()
