

from heapq import heappush, heappop
try:
    from gisutil import haversine
except:
    from util import haversine

class GraphSearchAnimator(object):
    """ Draw a graph search. """

    def __init__(self, graph, vertex_coords, quadtree):
        self.graph = graph
        self.vertex_coords = vertex_coords
        self.qtree = quadtree

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
        path = [self.vertex_coords[v] for v in path]
        return path

    def _sequence_coords(self, seq):
        """ 

        """
        needed = {}
        for node, actions in seq:
            needed[node] = self.vertex_coords[node]
            for arc in actions:
                needed[arc] = self.vertex_coords[arc]
        return needed

    def _find_closest_vertex(self, target, rng=.01):
        """ 
        Using the query_range function of the given quadtree, locate a vertex
        in the graph that is closest to the given point.

        Arguments:
        target -- (x, y) point to be matched to the graph.

        Returns:
        The ID of the vertex that is closest to the given point.
        """
        x, y = target
        close_vertices = self.qtree.query_range(x - rng, x + rng, y - rng, y + rng)
        best_vertex = None
        best_dist = float("inf")
        for point, vertices in close_vertices.iteritems():
            dist = haversine(point[0], point[1], target[0], target[1])
            if dist < best_dist:
                best_dist = dist
                best_vertex = vertices[0]
        return best_vertex

    def _dist(self, id1, id2):
        """ 
        Returns the distance in KM between the two ID'd vertices.

        Arguments:
        id1, id2 -- IDs matching vertices in self.vertex_coords
        """
        p1 = self.vertex_coords[id1]
        p2 = self.vertex_coords[id2]
        return haversine(p1[0], p1[1], p2[0], p2[1])
