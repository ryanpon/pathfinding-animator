
import os 
import sys
from flask import Flask, make_response, request
import json

app = Flask(__name__)
app.debug = False
# home for EC2 instance
PATH = "/home/ubuntu/blag/"
if "test" in sys.argv:
    app.debug = True
    PATH = ""
sys.path.append(PATH + "routing/")
from Quadtree import point_dict_to_quadtree
from astar import AStarAnimator
from bidirectional import BidirectionalAStarAnimator

with open(PATH + "routing/sf.j") as fp:
    graph = json.loads(fp.read())
with open(PATH + "routing/sf_coords.j") as fp:
    graph_coords = json.loads(fp.read())
with open(PATH + "routing/lm_dists.j") as fp:
    lm_dists = json.loads(fp.read())
quadtree = point_dict_to_quadtree(graph_coords, multiquadtree=True)
BIDIRECTION = BidirectionalAStarAnimator(graph, graph_coords, quadtree, lm_dists)
ANIMATOR = AStarAnimator(graph, graph_coords, quadtree, lm_dists)


@app.route("/")
def index():
    return open(PATH + "static/index.html", "r").read()

@app.route("/static/resume.pdf")
def get_resume():
    response = make_response(open(PATH + "static/resume.pdf", "r").read())
    response.headers["Content-Type"] = "application/pdf"
    return response

@app.route("/animation")
def search_animation():
    print request.args
    search_type = request.args.get("type")
    source = split_comma_ll(request.args.get("source"))
    dest = split_comma_ll(request.args.get("dest"))
    animator = ANIMATOR
    if request.args.get("bidirectional") == "true":
        animator = BIDIRECTION
    if search_type == "dijkstra":
        seq, coords, path = animator.dijkstra_animation(source, dest)
    elif search_type == "astar":
        seq, coords, path = animator.astar_animation(source, dest)
    elif search_type == "alt":
        seq, coords, path = animator.alt_animation(source, dest)
    response = {
        "sequence" : seq,
        "coords" : coords,
        "path" : path
    }
    return json.dumps(response)

@app.route("/test")
def test():
    return open(PATH + "static/gmaps.html", "r").read()

def split_comma_ll(ll_string):
    s = ll_string.split(",")
    return float(s[0]), float(s[1])

if __name__ == "__main__":
    app.run()
