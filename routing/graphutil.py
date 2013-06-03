
try:
    from gisutil import haversine
except:
    from util import haversine
from quadtree import point_dict_to_quadtree

class GraphUtil(object):
    """ 
    A class providing basic functionality over a { id : (lat, lon) } dict.
    """

    def __init__(self, vertex_coords):
        """ 
        Arguments:
        vertex_coords -- dict of the form: { id : (lat, lon) }
        """
        self.coords = vertex_coords
        # create a quadtree that can store multiple data per (lat, lon)
        self.qtree = point_dict_to_quadtree(vertex_coords, multiquadtree=True)

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

    def _euclidean(self, id1, id2):
        """ 
        Returns the distance in KM between the two ID'd vertices.

        Arguments:
        id1, id2 -- IDs matching vertices in self.coords
        """
        x1, y1 = self.coords[id1]
        x2, y2 = self.coords[id2]
        return haversine(x1, y1, x2, y2)

    def _manhattan(self, id1, id2):
        """ 
        Returns the Manhattan distance in KM between the two ID'd vertices.

        (x1, y1)
        [1]
         |
         |
         |
         |            (x2, y2) 
        [3]-----------[2]
        (x1, y2)

        returns dist(1, 3) + dist(2, 3)
        """
        x1, y1 = self.coords[id1]
        x2, y2 = self.coords[id2]
        x3, y3 = x1, y2
        return haversine(x3, y3, x2, y2) + haversine(x3, y3, x1, y1)

    def _octile(self, id1, id2):
        """ 
        Returns the octile distance in KM between the two ID'd vertices.
        
        (x1, y1)
        [1]
         |
         |
         |
        [3]
         | .
         |   .      
         |     .
         |       .
         |         .
         |       45( .   
        [ ]----------[2]
     
        returns dist(1, 3) + dist(2, 3)
        """
        x1, y1 = self.coords[id1]
        x2, y2 = self.coords[id2]
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        if dx > dy:
            x3 = max(x1, x2) - dy
            y3 = y1
        elif dx > dy:
            x3 = x1 
            y3 = max(y1, y2) - dx
        else:
            return haversine(x1, y1, x2, y2)
        return haversine(x3, y3, x2, y2) + haversine(x3, y3, x1, y1)
