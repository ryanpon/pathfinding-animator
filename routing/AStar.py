#Copyright (c) 2013 Ryan Pon
#Licensed under the MIT license.

"""

"""

try:
    import simplejson as json
except ImportError:
    import json
from heapq import heappush, heappop
from util import HeapSet
from Quadtree import point_dict_to_quadtree
from collections import defaultdict
from util import haversine
# import zlib

def exact_dist(source, dest, graph, coords):
    pred_list = {source : 0}
    closed_set = set()
    unseen = [(0, source)]    # keeps a set and heap structure
    while unseen:
        dist, vert = heappop(unseen)
        if vert in closed_set:
            continue
        elif vert == dest:
            return dist
        closed_set.add(vert)
        for arc, arc_len in graph[vert]:
            if arc not in closed_set:
                new_dist = (pred_list[vert] + arc_len)
                if arc not in pred_list or new_dist < pred_list[arc]:
                    pred_list[arc] = new_dist
                    est = new_dist + haversine(coords[arc][0], coords[arc][1], 
                                               coords[dest][0], coords[dest][1])
                    heappush(unseen, (est, arc))
    return None    # no valid path found


class PathfindingAnimator(object):
    """ Animation methods provide the means to draw a graph search. """

    def __init__(self, graph, vertex_coords, landmark_dict=None):
        self.graph = graph
        self.vertex_coords = vertex_coords
        self.landmark_dict = landmark_dict    # for ALT
        self.qtree = point_dict_to_quadtree(vertex_coords, multiquadtree=True)

    def astar_animation(self, source, dest, epsilon=1):
        source, dest = self.__find_nearest_vertices(source, dest)
        heuristic = lambda id1, id2: self.__dist(id1, id2) * epsilon
        seq, pred_list = self.__astar(source, dest, heuristic)
        return self.__process_search_result(seq, pred_list, dest)

    def dijkstra_animation(self, source, dest):
        source, dest = self.__find_nearest_vertices(source, dest)
        # no heurisitic, so just return zero
        heuristic = lambda id1, id2: 0
        seq, pred_list = self.__astar(source, dest, heuristic)
        return self.__process_search_result(seq, pred_list, dest)

    def alt_animation(self, source, dest):
        """ A* Landmark Triangle Inequality: ALT Algorithm """
        pass

    def __process_search_result(self, sequence, pred_list, dest):
        sequence_coords = self.__sequence_coords(sequence)
        path = self.__construct_shortest_path(pred_list, dest)
        return sequence, sequence_coords, path

    def __astar(self, source, dest, heuristic):
        sequence = []
        pred_list = {source : {'dist' : 0, 'pred' : None}}
        closed_set = set()
        unseen = [(0, source)]    # keeps a set and heap structure
        while unseen:
            _, vert = heappop(unseen)
            if vert in closed_set:
                continue
            elif vert == dest:
                return sequence, pred_list
            closed_set.add(vert)
            subseq = self.__relax_vertex(vert, dest, pred_list, 
                                          unseen, closed_set, heuristic)
            if subseq:
                sequence.append((vert, subseq))
        return None    # no valid path found

    def __relax_vertex(self, vert, dest, pred_list, 
                        unseen, closed_set, heuristic):
        subseq = []
        for arc, arc_len in self.graph[vert]:
            if arc in closed_set: 
                continue    # disgard nodes that already have optimal paths
            new_dist = pred_list[vert]['dist'] + arc_len
            if arc not in pred_list or new_dist < pred_list[arc]['dist']:
                # the shortest path to the arc changed, record this
                subseq.append(arc)
                pred_list[arc] = {'pred' : vert, 'dist' : new_dist}
                est = new_dist + heuristic(arc, dest)
                heappush(unseen, (est, arc))
        return subseq

    def __construct_shortest_path(self, pred_list, dest):
        path = []
        vertex = dest
        while pred_list[vertex]['pred'] is not None:
            path.append(vertex)
            vertex = pred_list[vertex]['pred']
        path.reverse()
        path = [self.vertex_coords[v] for v in path]
        return path

    def __sequence_coords(self, seq):
        needed = {}
        for node, actions in seq:
            needed[node] = self.vertex_coords[node]
            for arc in actions:
                needed[arc] = self.vertex_coords[arc]
        return needed

    def __find_nearest_vertices(self, source, dest):
        src_node = find_closest_node(source, self.qtree)
        dest_node = find_closest_node(dest, self.qtree)
        return src_node, dest_node

    def __dist(self, id1, id2):
        p1 = self.vertex_coords[id1]
        p2 = self.vertex_coords[id2]
        return haversine(p1[0], p1[1], p2[0], p2[1])


def load_graph():
    with open('sf.j', 'r') as fp:
        graph = json.loads(fp.read())
    with open('sf_coords.j', 'r') as fp:
        graph_coords = json.loads(fp.read())
    return graph, graph_coords

def find_closest_node(target, quadtree, rng=.01):
    x, y = target
    close_nodes = quadtree.query_range(x - rng, x + rng, y - rng, y + rng)
    best_node = None
    best_dist = float("inf")
    for point, nodes in close_nodes.iteritems():
        dist = haversine(point[0], point[1], target[0], target[1])
        if dist < best_dist:
            best_dist = dist
            best_node = nodes
    return best_node[0]

def animation(src, dest):
    graph, graph_coords = load_graph()
    animator = PathfindingAnimator(graph, graph_coords)
    seq, pred, d = astar_animation(src_node, dest_node, graph, graph_coords)
    seq = add_coords_to_seq(seq, graph_coords)
    with open('seq.j', 'w') as fp:
        fp.write(json.dumps(seq))

def landmark_distances(landmarks, graph, graph_coords):
    qtree = point_dict_to_quadtree(graph_coords, multiquadtree=True)
    lm_dists = defaultdict(list)
    l = len(graph_coords)
    for i, pid in enumerate(graph_coords):
        print i, '/', l, ':', pid
        for landmark in landmarks:
            d = exact_dist(pid, landmark, graph, graph_coords)
            lm_dists[pid].append(d)
    with open('lm_dists.j', 'w') as fp:
        fp.write(json.dumps(lm_dists))
    return lm_dists

def main():
    graph, graph_coords = load_graph()
    qtree = point_dict_to_quadtree(graph_coords, multiquadtree=True)
    landmarks = [(37.779941,-122.511292),
                 (37.71506,-122.484856),
                 (37.807343,-122.406235),
                 (37.726058,-122.379627)]
    landmarks = [find_closest_node(l, qtree) for l in landmarks]
    lm_dists = landmark_distances(landmarks, graph, graph_coords)

if __name__ == '__main__':
    #import cProfile
    #cProfile.run("main()", sort=1)
    pass