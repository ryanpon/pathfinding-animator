

from heapq import heappush, heappop
from animator import GraphSearchAnimator


class AStarAnimator(GraphSearchAnimator):
    """ Draw a graph search. """

    def __init__(self, graph, vertex_coords, quadtree, landmark_dict):
        GraphSearchAnimator.__init__(self, graph, vertex_coords, quadtree)
        self.landmark_dict = landmark_dict    # for ALT

    def astar_animation(self, source, dest, heuristic, epsilon=1, p=1.414):
        source = self._find_closest_vertex(source)
        dest = self._find_closest_vertex(dest)
        h_fun = self._heuristic_selector(heuristic, p)
        h = lambda v: h_fun(v, dest) * epsilon
        seq, pred_list = self.__astar(source, dest, h)
        return self.__process_search_result(seq, pred_list, dest)

    def dijkstra_animation(self, source, dest):
        source = self._find_closest_vertex(source)
        dest = self._find_closest_vertex(dest)
        # no heurisitic, so just return zero
        h = lambda v: 0
        seq, pred_list = self.__astar(source, dest, h)
        return self.__process_search_result(seq, pred_list, dest)

    def alt_animation(self, source, dest, epsilon=1):
        """ A* Landmark Triangle Inequality: ALT Algorithm """
        source = self._find_closest_vertex(source)
        dest = self._find_closest_vertex(dest)
        # no heurisitic, so just return zero
        h = lambda v: self.__alt_heuristic(v, dest) * epsilon
        seq, pred_list = self.__astar(source, dest, h)
        return self.__process_search_result(seq, pred_list, dest)

    def __process_search_result(self, sequence, pred_list, dest):
        sequence_coords = self._sequence_coords(sequence)
        path = self._construct_shortest_path(pred_list, dest)
        return sequence, sequence_coords, path

    def __astar(self, source, dest, h):
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
            subseq = self.__relax_vertex(vert, dest, pred_list, 
                                          unseen, closed_set, h)
            #if subseq:
            #    sequence.append((vert, subseq))
        return None    # no valid path found

    def __relax_vertex(self, vert, dest, pred_list, 
                        unseen, closed_set, h):
        subseq = []
        for arc, arc_len in self.graph[vert]:
            if arc in closed_set: 
                continue    # disgard nodes that already have optimal paths
            new_dist = pred_list[vert]['dist'] + arc_len
            if arc not in pred_list or new_dist < pred_list[arc]['dist']:
                # the shortest path to the arc changed, record this
                subseq.append(arc)
                pred_list[arc] = {'pred' : vert, 'dist' : new_dist}
                est = new_dist + h(arc)
                heappush(unseen, (est, arc))
        return subseq

    def __alt_heuristic(self, id1, id2):
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
