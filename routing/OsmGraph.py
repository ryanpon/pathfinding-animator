"""

"""

import sys
sys.path.append("pyroutelib/")
from loadOsm import LoadOsm 
sys.path.append("quadtree")
try:
    import simplejson as json
except ImportError:
    import json
from collections import defaultdict
from util import haversine

# osmosis --read-xml file="sf.osm" --bounding-box top=37.816 bottom=37.704 left=-122.525 right=-122.352 --write-xml file="sf2.osm"

def process_osm(osm_path):
    """ 
    Split the object from pyroutelib into two dicts:
    - adjlist with node_id --> list of edges
    - dict of node_id : (lat, lon)
    """
    osm = load_osm(osm_path)
    graph = osm.routing['foot']
    node_coords = osm.nodes
    #routeable = osm.routeableNodes
    adjlist, node_coords = simple_adjlist(graph, node_coords)
    return adjlist, node_coords

def load_osm(osm_path):
    """ 
    Use pyroutelib to load OSM data into native data structures. 

    Needed fields from LoadOsm object:
    .nodes -- locations of nodes
    .routeTypes -- use to check that 'foot' exists
    .routeableNodes -- use to populate Quadtree
    .routing -- the graph itself
    """
    osm = LoadOsm(osm_path)
    assert 'foot' in osm.routeTypes, "This OSM data has no walking routes!"
    return osm

def simple_adjlist(graph, node_coords):
    """ """
    adjlist = defaultdict(list)
    needed_coords = {}
    for node in (n for n in graph if n in node_coords):
        needed_coords[node] = node_coords[node]
        for edge in (e for e in graph[node] if e in node_coords):
            needed_coords[str(edge)] = node_coords[edge]
            p1 = node_coords[node]
            p2 = node_coords[edge]
            e_tuple = str(edge), haversine(p1, p2)
            adjlist[str(node)].append(e_tuple)
    return dict(adjlist), needed_coords

if __name__ == '__main__':
    adjlist, node_coords = process_osm('sf.osm')
    with open('sf.j', 'w') as fp:
        fp.write(json.dumps(adjlist))
    with open('sf_coords.j', 'w') as fp:
        fp.write(json.dumps(node_coords))
