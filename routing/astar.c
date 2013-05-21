
#include "Python.h"
#include <queue>

static PyObject *AStarError;

/*
Calculates the great circle distance between two points on the surface of the
Earth and returns a result in kilometers.
*/
static double
haversine(double lat1, double lon1, double lat2, double lon2)
{
    double s_dlat, s_dlon, a, c;
    // Convert latitude and longitude to radians before we do anything.
    lat1 = radians(lat1);
    lon1 = radians(lon1);
    lat2 = radians(lat2);
    lon2 = radians(lon2);

    s_dlat = sin((lat2 - lat1) / 2);
    s_dlon = sin((lon2 - lon1) / 2);

    a = s_dlat * s_dlat + s_dlon * s_dlon * cos(lat1) * cos(lat2);
    c = 2 * asin(sqrt(a));
    return c * 6367;
}


/*
def exact_dist(source, dest, graph, coords):
    pred_list = {source : {'dist' : 0}}
    closed_set = set()
    unseen = HeapSet()    # keeps a set and heap structure
    unseen.push(0, source)
    while unseen:
        # vert is a string
        dist, vert = unseen.pop()
        closed_set.add(vert)
        if vert == dest:
            return dist
        for arc, length in graph[vert]:
            if arc in closed_set:
                continue
            new_dist = (pred_list[vert]['dist'] + length)
            if arc not in unseen or new_dist < pred_list[arc]['dist']:
                pred_list[arc] = {'pred' : vert, 'dist' : new_dist}
                if arc not in unseen:
                    est = new_dist + distance(arc, dest, coords)
                    unseen.push(est, arc)
    print "Couldn't find a path between source and dest."
    return None
*/

static PyObject *
astar(PyObject *self, PyObject *args) {
    char *source, *dest;     // the source and destination vertice IDs
    PyObject *graph;         // dict: { vert_id : (arc_id, arc_len) } 
    PyObject *coords;        // dict: { vert_id : (lat, lon) }
    PyObject *pred_list;     // dict: { vert_id : dist_from_origin }
    PyObject *unseen;        // nodes to expand next
    PyObject *unseen_set;    // set: test membership for unseen
    PyObject *closed_set;    // set: nodes already expanded
    if (!PyArg_ParseTuple(args, "ssoo", source, dest, graph, coords)) {
        return NULL;
    }
    return NULL;
}


/* Define Methods */

static PyMethodDef module_methods[] = {
    {"astar", (PyCFunction)astar, METH_VARARGS, " "},
    {NULL}
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initastar(void) 
{
    PyObject* m;
    m = Py_InitModule("astar", module_methods);
    if (m == NULL)
        return;
    
    AStarError = PyErr_NewException("astar.error", NULL, NULL);
    Py_INCREF(AStarError);
    PyModule_AddObject(m, "error", AStarError);
}
