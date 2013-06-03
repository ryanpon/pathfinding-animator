/*
This module provides a number of functions which are useful when doing GIS 
related calculations.
*/

#include <Python.h>
#include <math.h>

static PyObject *UtilError;

static inline double radians(double degrees) {return degrees * M_PI / 180;}
static inline double degrees(double radians) {return radians * 180.0 / M_PI;}

/*
Calculates the great circle distance between two points on the surface of the
Earth and returns a result in kilometers.
*/
static PyObject *
haversine(PyObject *self, PyObject *args)
{
    double lat1, lon1, lat2, lon2;
    if (!PyArg_ParseTuple(args, "dddd", &lat1, &lon1, &lat2, &lon2)) {
        return NULL;
    }
    // Convert latitude and longitude to radians before we do anything.
    lat1 = radians(lat1);
    lon1 = radians(lon1);
    lat2 = radians(lat2);
    lon2 = radians(lon2);

    double dlat = lat2 - lat1;
    double dlon = lon2 - lon1;
    double s_dlat = sin(dlat/2);
    double s_dlon = sin(dlon/2);

    double a = s_dlat * s_dlat + s_dlon * s_dlon * cos(lat1) * cos(lat2);
    double c = 2 * asin(sqrt(a));
    PyObject *km = Py_BuildValue("d", (c * 6367));
    return km;
}

/*
Calculates the absolute bearing of the line between 
(lat1, lon1) to (lat2, lon2). The fifth argument is a boolean, pos.
If pos is true, the range of bearing returned will be between 0 and 360.
Otherwise, it will be between -180 and 180.
*/
static PyObject *
bearing(PyObject *self, PyObject *args)
{
    double lat1, lon1, lat2, lon2;
    short pos;    // -180 to 180 vs 0 to 360
    if (!PyArg_ParseTuple(args, "ddddb", &lat1, &lon1, &lat2, &lon2, &pos)) 
    {
        return NULL;
    }
    double d_lon = lon2 - lon1;
    double x = sin(d_lon) * cos(lat2);
    double y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(d_lon);
    double bearing = degrees(atan2(x, y));
    if (pos && bearing < 0) {
        bearing += 360;
    }
    return Py_BuildValue("d", bearing);
}

/*
Calculates the smallest angle between two bearings. The result will be provided 
as a positive double between 0 and 180.
*/
static PyObject *
bearing_angle(PyObject *self, PyObject *args)
{
    double brng1, brng2, result;
    if (!PyArg_ParseTuple(args, "dd", &brng1, &brng2)) {
        return NULL;
    }
    if ((brng1 >= 0 && brng2 >= 0) || (brng1 <= 0 && brng2 <= 0)) {
        return Py_BuildValue("d", fabs(brng1 - brng2));
    }
    result = 0;
    if (brng1 < 0) {
        result = fabs(180 + brng1) + (180 - brng2);
    } else {
        result = fabs(180 + brng2) + (180 - brng1);
    }
    if (result > 180) {
        result = fabs(result - 360);
    }
    return Py_BuildValue("d", result);
}

/*
Calculates the Euclidean distance between two points.

This function is only marginally faster than the pure Python version. Due to 
function call overhead, it is likely slower than inlined Python.
*/
static PyObject *
edistance(PyObject *self, PyObject *args)
{
    double lat1, lon1, lat2, lon2;
    if (!PyArg_ParseTuple(args, "dddd", &lat1, &lon1, &lat2, &lon2)) {
        return NULL;
    }
    return Py_BuildValue(
            "d", sqrt(pow((lat1 - lat2), 2) + pow((lon1 - lon2), 2)));
}

/* Define Methods */

static PyMethodDef module_methods[] = {
    {"haversine", (PyCFunction)haversine, METH_VARARGS, " "},
    {"bearing", (PyCFunction)bearing, METH_VARARGS, " "},
    {"edistance", (PyCFunction)edistance, METH_VARARGS, " "},
    {"bearing_angle", (PyCFunction)bearing_angle, METH_VARARGS, " "},
    {NULL}
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initgisutil(void) 
{
    PyObject* m;
    m = Py_InitModule("gisutil", module_methods);
    if (m == NULL)
        return;
    
    UtilError = PyErr_NewException("util.error", NULL, NULL);
    Py_INCREF(UtilError);
    PyModule_AddObject(m, "error", UtilError);
}
