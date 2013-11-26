
from __future__ import division
from heapq import heappush, heappop
try:
    from gisutil import haversine
except:
    from util import haversine
from graphutil import GraphUtil

class GraphSearchAnimator(object):
    """ Draw a graph search. """

    def __init__(self, graph, vertex_coords):
        """ 

        """
        self.graph = graph
        self.util = GraphUtil(vertex_coords)

    def _astar(self, source, dest, h):
        """
        Implemented by objects that inherit from this.
        """
        pass

    def _animation(self, source, dest, heuristic):
        seq, pred_list = self._astar(source, dest, heuristic)
        return self._process_search_result(seq, pred_list, dest)

    def _process_search_result(self, sequence, pred_list, dest):
        sequence_coords = self._sequence_coords(sequence)
        path = self._construct_shortest_path(pred_list, dest)
        return sequence, sequence_coords, path

    def _find_source_dest(self, source, dest):
        s_vertex = self.util._find_closest_vertex(source)
        d_vertex = self.util._find_closest_vertex(dest)
        return s_vertex, d_vertex

    def _construct_shortest_path(self, pred_list, dest):
        """ 
        Given a predecessor list, such as created by A*, and the dest
        vertex ID, return the shortest path found by the algorithm.

        Will likely have to been overriden in the case of bidirectional
        algorithms.
        """
        path = []
        vertex = dest
        while pred_list[vertex]['pred'] is not None:
            path.append(vertex)
            vertex = pred_list[vertex]['pred']
        path.reverse()
        path = [self.util.coords[v] for v in path]
        return path

    def _sequence_coords(self, seq):
        """ 

        """
        needed = {}
        coords = self.util.coords
        for vertex, actions in seq:
            needed[vertex] = coords[vertex]
            for arc in actions:
                needed[arc] = coords[arc]
        return needed

    def _heuristic_selector(self, heuristic):
        h_fun = self.util._euclidean
        if heuristic == "manhattan":
            h_fun = self.util._manhattan
        elif heuristic == "octile":
            h_fun = self.util._octile
        return h_fun            

    def _alt_heuristic(self, id1, id2):
        max_dist = 0
        lm_dists = self.landmark_dict
        for dist1, dist2 in zip(lm_dists[id1], lm_dists[id2]):
            try:
                d = abs(dist1 - dist2)
                if d > max_dist:
                    max_dist = d
            except TypeError:
                # Some nodes couldnt reach a landmark
                pass
        return max_dist
