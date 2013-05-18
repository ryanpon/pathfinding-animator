#Copyright (c) 2012 Ryan Pon
#Licensed under the MIT license.

"""

"""

try:
    import simplejson as json
except ImportError:
    import json
from util import haversine, HeapSet

CHANGE_PRED = 0
CONSIDER = 1
    
def astar_animation(source, dest, graph, coords):
    def distance(id1, id2):
        return haversine(coords[id1], coords[id2])
    sequence = []
    pred_list = {source : {'dist' : 0}}
    closed_set = set()
    unseen = HeapSet()    # keeps a set and heap structure
    unseen.push(0, source)
    while unseen:
        _ , vertex = unseen.pop()
        closed_set.add(vertex)
        if vertex == dest:
            break
        # keep a record of the actions taken
        subseq = []
        # following block should be subfunction
        for edge, length in graph[vertex]:
            if edge in closed_set:
                continue
            # consider this edge as a candidate for shortest paths
            subseq.append((edge, CONSIDER))
            new_dist = (pred_list[vertex]['dist'] + length)
            if edge not in unseen or new_dist < pred_list[edge]['dist']:
                # the shortest path to the edge changed, record this
                subseq.append((edge, CHANGE_PRED))
                pred_list[edge] = {'pred' : vertex, 'dist' : new_dist}
                est = (new_dist + distance(edge, dest))
                if edge not in unseen:
                    unseen.push(est, edge)

        if subseq:
            sequence.append((vertex, subseq))
    return sequence, pred_list

def add_coords_to_seq(seq, coords):
    needed = {}
    for node, actions in seq:
        needed[node] = coords[node]
        for edge, _ in actions:
            needed[edge] = coords[edge]
    return [seq, needed]

def load_graph():
    with open('sf.j', 'r') as fp:
        graph = json.loads(fp.read())
    with open('sf_coords.j', 'r') as fp:
        graph_coords = json.loads(fp.read())
    return graph, graph_coords

if __name__ == '__main__':
    graph, graph_coords = load_graph()
    seq, pred = astar_animation('633145456', '367017154', graph, graph_coords)
    seq = add_coords_to_seq(seq, graph_coords)
    with open('seq.j', 'w') as fp:
        fp.write(json.dumps(seq))
