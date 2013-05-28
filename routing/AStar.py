#Copyright (c) 2013 Ryan Pon
#Licensed under the MIT license.

"""

"""

try:
    import simplejson as json
except ImportError:
    import json
from heapq import heappush, heappop
from Quadtree import point_dict_to_quadtree
from collections import defaultdict
try:
    # my C module for basic GIS stuff
    from gisutil import haversine, bearing
except ImportError:
    from util import haversine, bearing

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
    if best_node:
        return best_node[0]
    else: 
        return None

def exact_dist(source, dest, graph, coords):
    dest_x, dest_y = coords[dest]
    pred_list = {source : 0}
    closed_set = set()
    unseen = [(0, source)]    # keeps a set and heap structure
    while unseen:
        _, vert = heappop(unseen)
        if vert in closed_set:
            # needed because we dont have a heap with decrease-key
            continue
        elif vert == dest:
            return pred_list[vert]
        closed_set.add(vert)
        for arc, arc_len in graph[vert]:
            if arc not in closed_set:
                new_dist = (pred_list[vert] + arc_len)
                if arc not in pred_list or new_dist < pred_list[arc]:
                    pred_list[arc] = new_dist
                    x, y = coords[arc]
                    heappush(unseen, (new_dist + haversine(x, y, dest_x, dest_y), arc))
    return None    # no valid path found

def lm_exact_dist(source, dest, graph, coords, lm_dists):
    """ Speed up by using already calculated euclidean distance. """
    lm_dists = lm_dists[dest]
    pred_list = {source : 0}
    closed_set = set()
    unseen = [(0, source)]    # keeps a set and heap structure
    while unseen:
        _, vert = heappop(unseen)
        if vert in closed_set:
            # needed because we dont have a heap with decrease-key
            continue
        elif vert == dest:
            return pred_list[vert]
        closed_set.add(vert)
        for arc, arc_len in graph[vert]:
            if arc not in closed_set:
                new_dist = (pred_list[vert] + arc_len)
                if arc not in pred_list or new_dist < pred_list[arc]:
                    pred_list[arc] = new_dist
                    heappush(unseen, (new_dist + lm_dists[arc], arc))
    return None    # no valid path found

def landmark_distances(landmarks, graph, graph_coords):
    lm_est = {}
    for lm_id, lm_coord in landmarks:
        lm_est[lm_id] = {}
        x,y = lm_coord
        for pid, coord in graph_coords.iteritems():
            lm_est[lm_id][pid] = haversine(x, y, coord[0], coord[1])
    qtree = point_dict_to_quadtree(graph_coords, multiquadtree=True)
    lm_dists = defaultdict(list)
    l = len(graph_coords)
    for i, pid in enumerate(graph_coords):
        print i, '/', l, ':', pid
        for landmark, _ in landmarks:
            try:
                d = lm_exact_dist(pid, landmark, graph, graph_coords, lm_est)
            except KeyError:
                d = None
            lm_dists[pid].append(d)
    return lm_dists

def planar_landmark_selection(k, origin, coords, graph, qtree):
    origin_id = find_closest_node(origin, qtree)
    origin = coords[origin_id]
    sectors = section_plane(k, origin, coords)
    landmarks = []
    for sector in sectors:
        max_dist = float("-inf")
        best_candidate = None
        for pid, coord in sector:
            cur_dist = haversine(origin[0], origin[1], coord[0], coord[1])
            if cur_dist > max_dist and exact_dist(pid, origin_id, graph, coords):
                max_dist = cur_dist
                best_candidate = coord
        landmarks.append(best_candidate)
    return landmarks

def section_plane(k, origin, coords):
    sectors = [[] for _ in xrange(k)]        
    sector_size = 360.0 / k
    for pid, coord in coords.iteritems():
        b = bearing(origin[0], origin[1], coord[0], coord[1], True)
        s = int(b / sector_size)
        sectors[s].append((pid, coord))
    return sectors

def farthest_landmark_selection(k, origin, coords):
    landmarks = [origin]
    for _ in xrange(k):
        max_dist = float("-inf") 
        best_candidate = None
        for pid, coord in coords.iteritems():
            cur_dist = 0
            for lm in landmarks:
                cur_dist += haversine(lm[0], lm[1], coord[0], coord[1])
            if cur_dist > max_dist and not coord in landmarks:
                max_dist = cur_dist
                best_candidate = coord
        landmarks.append(best_candidate)
        if len(landmarks) > k:
            landmarks.pop(0)
    return landmarks

def load_graph():
    with open('sf.j', 'r') as fp:
        graph = json.loads(fp.read())
    with open('sf_coords.j', 'r') as fp:
        graph_coords = json.loads(fp.read())
    return graph, graph_coords


from multiprocessing import Queue, Process, Value
import math

def mp_landmark_distances(landmarks, graph, graph_coords, nprocs):
    def worker(landmarks, graph, graph_coords, pids, out_q, counter):
        """ The worker function, invoked in a process. 'nums' is a
            list of numbers to factor. The results are placed in
            a dictionary that's pushed to a queue.
        """
        lm_est = {}
        for lm_id, lm_coord in landmarks:
            lm_est[lm_id] = {}
            x,y = lm_coord
            for pid, coord in graph_coords.iteritems():
                lm_est[lm_id][pid] = haversine(x, y, coord[0], coord[1])
        qtree = point_dict_to_quadtree(graph_coords, multiquadtree=True)
        lm_dists = defaultdict(list)
        l = len(graph_coords)
        for pid in pids:
            counter.value += 1
            print counter.value, '/', l, ':', pid
            for landmark, _ in landmarks:
                try:
                    d = lm_exact_dist(pid, landmark, graph, graph_coords, lm_est)
                except KeyError:
                    d = None
                lm_dists[pid].append(d)
        out_q.put(lm_dists)

    # Each process will get 'chunksize' nums and a queue to put his out
    # dict into
    counter = Value("i")
    all_pids = graph_coords.keys()
    out_q = Queue()
    chunksize = int(math.ceil(len(all_pids) / float(nprocs)))
    procs = []

    for i in range(nprocs):
        chunk = all_pids[chunksize * i:chunksize * (i + 1)]
        p = Process(
                target=worker,
                args=(landmarks, graph, graph_coords, chunk, out_q, counter)
            )
        procs.append(p)
        p.start()

    # Collect all results into a single result dict. We know how many dicts
    # with results to expect.
    resultdict = {}
    for i in range(nprocs):
        resultdict.update(out_q.get())

    # Wait for all worker processes to finish
    for p in procs:
        p.join()
    return resultdict

def main():
    graph, graph_coords = load_graph()
    origin = 37.772614,-122.423798
    k = 16
    qtree = point_dict_to_quadtree(graph_coords, multiquadtree=True)
    landmarks = planar_landmark_selection(k, origin, graph_coords, graph, qtree)
    # create a quadtree that can hold multiple items per point
    
    landmarks = zip([find_closest_node(l, qtree) for l in landmarks], landmarks)
    lm_dists = mp_landmark_distances(landmarks, graph, graph_coords, 8)
    with open('lm_dists_2.j', 'w') as fp:
        fp.write(json.dumps(lm_dists))

if __name__ == '__main__':
    main()
    # import cProfile
    # cProfile.run('main()', sort=1)
