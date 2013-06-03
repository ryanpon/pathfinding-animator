

from heapq import heappush, heappop
from animator import GraphSearchAnimator


class AStarAnimator(GraphSearchAnimator):
    """ Draw a graph search. """

    def __init__(self, graph, vertex_coords, landmark_dict):
        GraphSearchAnimator.__init__(self, graph, vertex_coords)
        self.landmark_dict = landmark_dict    # for ALT

    def astar_animation(self, source, dest, heuristic, epsilon=1):
        source, dest = self._find_source_dest(source, dest)
        h_fun = self._heuristic_selector(heuristic)
        h = lambda v: h_fun(v, dest) * epsilon
        return self._animation(source, dest, h)

    def dijkstra_animation(self, source, dest):
        source, dest = self._find_source_dest(source, dest)
        # no heurisitic, so just return zero
        h = lambda v: 0
        return self._animation(source, dest, h)

    def alt_animation(self, source, dest, epsilon=1):
        """ A* Landmark Triangle Inequality: ALT Algorithm """
        source, dest = self._find_source_dest(source, dest)
        h = lambda v: self._alt_heuristic(v, dest) * epsilon
        return self._animation(source, dest, h)

    def _astar(self, source, dest, h):
        if not source or not dest:
            return {}, [] 
        sequence = []
        pred_list = {source : {'dist' : 0, 'pred' : None}}
        closed_set = set()
        unseen = [(0, source)]    # keeps a set and heap structure
        while unseen:
            _, vert = heappop(unseen)
            sequence.append((pred_list[vert]['pred'], [vert]))
            if vert in closed_set:
                continue
            elif vert == dest:
                return sequence[1:], pred_list
            closed_set.add(vert)
            self._relax_vertex(vert, dest, pred_list, unseen, closed_set, h)
        return None    # no valid path found

    def _relax_vertex(self, vert, dest, pred_list, 
                        unseen, closed_set, h):
        for arc, arc_len in self.graph[vert]:
            if arc in closed_set: 
                continue    # disgard nodes that already have optimal paths
            new_dist = pred_list[vert]['dist'] + arc_len
            if arc not in pred_list or new_dist < pred_list[arc]['dist']:
                # the shortest path to the arc changed, record this
                pred_list[arc] = {'pred' : vert, 'dist' : new_dist}
                est = new_dist + h(arc)
                heappush(unseen, (est, arc))

    def _alt_heuristic(self, id1, id2):
        max_dist = float("-inf")
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
