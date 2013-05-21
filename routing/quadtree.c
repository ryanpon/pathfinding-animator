
#include "Python.h"
#include "quadtree.h"

typedef struct {
    PyObject_HEAD
    struct Quadtree *qtree;
} QT_Wrapper;

staticforward PyTypeObject QuadtreeType;

// Alloc / dealloc

static void
Quadtree_dealloc(QT_Wrapper *self)
{
    free_quadtree(self->qtree);
    self->qtree = NULL;
    self->ob_type->tp_free((PyObject*) self);
    mem_check();
}

static int
Quadtree_init(QT_Wrapper *self, PyObject *args, PyObject *kwds)
{
    int b = 40;                           // numbers of buckets
    double min_x, max_x, min_y, max_y;    // bounds
    min_x = max_x = min_y = max_y = 0;

    if (!PyArg_ParseTuple(args, "ddddi", &min_x, &max_x, &min_y, &max_y, &b))
        return -1;
    self->qtree = make_qtree(min_x, max_x, min_y, max_y, b);
    if (!self->qtree) return -1;
    return 0;
}
 
/* Methods */

static PyObject *
Quadtree_insert(QT_Wrapper *self, PyObject *args)
{
    double x, y;
    x = y = 0;
    int i = 0;
    if (!PyArg_ParseTuple(args, "ddi", &x, &y, &i))
        return NULL;
    struct PointData point =  {x, y, i};
    if (!insert(self->qtree, &point)) return Py_BuildValue("i", 1);
    else return Py_BuildValue("i", 0);
}

static PyObject *
Quadtree_query_range(QT_Wrapper *self, PyObject *args)
{
    double min_x, max_x, min_y, max_y;    // bounds
    min_x = max_x = min_y = max_y = 0;
    if (!PyArg_ParseTuple(args, "dddd", &min_x, &max_x, &min_y, &max_y))
        return NULL;
    struct ResultNode *raw;
    raw = query_range(self->qtree, min_x, max_x, min_y, max_y);
    PyObject *res = PyList_New(0);
    while (raw->prev) {
        PyList_Append(res, Py_BuildValue("(ddi)", raw->x, raw->y, raw->i));
        struct ResultNode *to_free = raw;
        raw = raw->prev;
        mem_free(to_free);
    }
    mem_free(raw);
    return res;
}

/* Define Methods */

static PyMethodDef module_methods[] = {
    {"insert", (PyCFunction)Quadtree_insert, METH_VARARGS, " "},
    {"query_range", (PyCFunction)Quadtree_query_range, METH_VARARGS, " "},
    {NULL}
};

/* Define Type */

static PyTypeObject QuadtreeType = {
    PyObject_HEAD_INIT(NULL)
    0,                              /*ob_size*/
    "Quadtree",                     /*tp_name*/
    sizeof(QT_Wrapper),               /*tp_basicsize*/
    0,                              /*tp_itemsize*/
    (destructor)Quadtree_dealloc,   /*tp_dealloc*/
    0,                              /*tp_print*/
    0,                              /*tp_getattr*/
    0,                              /*tp_setattr*/
    0,                              /*tp_compare*/
    0,                              /*tp_repr*/
    0,                              /*tp_as_number*/
    0,                              /*tp_as_sequence*/
    0,                              /*tp_as_mapping*/
    0,                              /*tp_hash */
    0,                              /*tp_call*/
    0,                              /*tp_str*/
    0,                              /*tp_getattro*/
    0,                              /*tp_setattro*/
    0,                              /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Quadtree spatial index",       /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    0,                              /* tp_iter */
    0,                              /* tp_iternext */
    module_methods,                 /* tp_methods */
    0,                              /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    (initproc)Quadtree_init,        /* tp_init */
    0,                              /* tp_alloc */
    PyType_GenericNew,              /* tp_new */
};

/* Initialization */

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initquadtree(void) 
{
    PyObject* m;
    if (PyType_Ready(&QuadtreeType) < 0)
        return;
    m = Py_InitModule3("quadtree", module_methods,
                       "Quadtree spatial index.");
    if (m == NULL)
      return;

    Py_INCREF(&QuadtreeType);
    PyModule_AddObject(m, "Quadtree", (PyObject *)&QuadtreeType);

}
