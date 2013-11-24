
import os 
import sys
from flask import Flask, make_response, request
from flask.ext.gzip import Gzip
import json

app = Flask(__name__)
gzip = Gzip(app, compress_level=9)
if "test" in sys.argv:
    app.debug = True
sys.path.append("routing/")
from astar import AStarAnimator
from bidirectional import BidirectionalAStarAnimator

with open("routing/graph_data/sf.j") as fp:
    graph = json.loads(fp.read())
with open("routing/graph_data/sf_coords.j") as fp:
    graph_coords = json.loads(fp.read())
with open("routing/graph_data/lm_dists.j") as fp:
    lm_dists = json.loads(fp.read())

BIDIRECTION = BidirectionalAStarAnimator(graph, graph_coords, lm_dists)
ANIMATOR = AStarAnimator(graph, graph_coords, lm_dists)


@app.route("/favicon.ico")
def get_favicon():
    return open("static/favicon.ico", "r").read()

@app.route("/animation")
def search_animation():
    search_type = request.args.get("type")
    source = split_comma_ll(request.args.get("source"))
    dest = split_comma_ll(request.args.get("dest"))
    try:
        epsilon = float(request.args.get("epsilon", 1))
        epsilon = epsilon if epsilon >= 0 else 1
    except ValueError:
        epsilon = 1
    heuristic = request.args.get("heuristic", "manhattan")

    animator = ANIMATOR
    if request.args.get("bidirectional") == "true":
        animator = BIDIRECTION
    if search_type == "dijkstra":
        seq, coords, path = animator.dijkstra_animation(source, dest)
    elif search_type == "astar":
        seq, coords, path = animator.astar_animation(source, dest, heuristic, epsilon)
    elif search_type == "alt":
        seq, coords, path = animator.alt_animation(source, dest, epsilon)
    data = {
        "sequence" : seq,
        "coords" : coords,
        "path" : path
    }

    return make_response(json.dumps(data))

@app.route("/animate")
def animate():
    return open("static/gmaps.html", "r").read()

@app.route("/")
def index():
    return open("static/index.html", "r").read()

@app.route("/static/resume.pdf")
def get_resume():
    response = make_response(open("static/resume.pdf", "r").read())
    response.headers["Content-Type"] = "application/pdf"
    return response

def split_comma_ll(ll_string):
    s = ll_string.split(",")
    return float(s[0]), float(s[1])

if __name__ == "__main__":
    app.run()
