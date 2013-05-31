

from animator import GraphSearchAnimator

class IterativeDeepeningAnimator(GraphSearchAnimator):
    """ Draw a graph search. """

    def __init__(self, graph, vertex_coords, quadtree):
        GraphSearchAnimator.__init__(self, graph, vertex_coords, quadtree)

    def ida_animation(self, source, dest, epsilon=1):
        source = self._find_closest_vertex(source)
        dest = self._find_closest_vertex(dest)
        heuristic = lambda v: self._dist(v, dest) * epsilon
        path, sequence = self.__ida(source, dest, heuristic)
        print path, sequence
        return self.__process_search_result(path, sequence)

    def __process_search_result(self, path, sequence):
        sequence_coords = self._sequence_coords(sequence)
        return [], sequence_coords, [self.vertex_coords[v] for v in path]

    def _sequence_coords(self, seq):
        """ 

        """
        needed = {}
        for node in seq:
            needed[node] = self.vertex_coords[node]
        return needed

    def __ida(self, source, dest, heuristic):
        # nextcb is the cost bound(cb) for the next iteration
        nextcb = heuristic(source)
        while True:
            cb, nextcb = nextcb, float("inf")
            stack = [self.__movegen(source, 0, heuristic)]
            while stack:
                top = stack[-1]
                if len(top) == 0:
                    # BACKTRACK
                    stack.pop()
                else:
                    h, g, v = top.pop() 
                    f = h + g
                    if f <= cb:
                        # ADVANCE!
                        if v == dest:
                            print "HOORAY"
                            return
                        stack.append(self.__movegen(v, g, heuristic))    
                    else:
                        if f < nextcb:
                            print v
                        nextcb = min(f, nextcb)

    def __movegen(self, v, g, heuristic):
        # generates all sons of state and returns them ordered according to h
        moves = []
        for s, arclen in self.graph[v]:
            s_g = g + arclen
            s_info = heuristic(s), s_g, s
            moves.append(s_info)
        return sorted(moves, reverse=True) 


if __name__ == "__main__":
