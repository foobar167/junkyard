// Warning: Visual Studio only supports C89. That means that all of your
// variables must be declared before anything else at the top of a function.
#include <Python.h>
// I think this means we're using the 1.13 API
// http://docs.scipy.org/doc/numpy/reference/c-api.deprecations.html
#define NPY_NO_DEPRECATED_API NPY_1_13_API_VERSION
#include <numpy/arrayobject.h>
#include <stdio.h>
#include <stdlib.h>

static PyObject *descriptor(PyObject *self, PyObject *args);
static PyObject *distance(PyObject *self, PyObject *args);

static PyMethodDef module_methods[] = {
    {"descriptor", descriptor, METH_VARARGS,
     "return descriptor of the image"},
    {"distance", distance, METH_VARARGS,
     "calculate distance between two descriptors and return it as an integer"},
    {NULL, NULL, 0, NULL}    // sentinel
};

PyMODINIT_FUNC initcomatrix(void) {
    if (!(Py_InitModule3("comatrix", module_methods,
	    "co-occurrence matrices module"))) return;
    import_array();  // something to do with numpy
}

static PyObject *descriptor(PyObject *self, PyObject *args) {
    // Return descriptor of the image
    unsigned int i, j, k, w, h, n, row, index, value, dx, dy;
    unsigned int *temp, *comatrix, *arr = NULL;
    unsigned short int rgb1, rgb2;  // 9-bit RGB color: 3+3+3 is red+green+blue
    unsigned short int ***image;  // input image array
    PyObject *input = NULL, *output = NULL;  // input and output arrays
    PyArray_Descr *descr;
    npy_intp dims1[1], dims3[3];

    // Expect a 3D array of image: width, height, colors
    if (!PyArg_ParseTuple(args, "O!II", &PyArray_Type, &input, &dx, &dy)) return NULL;

    // Create C array from numpy object. Convert uint8 to uint16
    // for the future RGB calculation.
    descr = PyArray_DescrFromType(NPY_UINT16);  // unsigned short int
    if (PyArray_AsCArray(&input, (void ***)&image, dims3, 3, descr) < 0) {
        PyErr_SetString(PyExc_TypeError, "error converting to c array");
        return NULL;
    }

    // Create the 2D array, diagonal co-occurrence matrix of 512x512 or 2^9*2^9 or 2^18
    if (!(comatrix = (unsigned int *) malloc((2<<18) * sizeof(unsigned int)))) return NULL;
    memset (comatrix, 0, (2<<18) * sizeof(unsigned int));  // zeroize co-matrix

    w = dims3[1] - dx;  // image width
    h = dims3[0] - dy;  // image height
    n = 0;  // number of non-zero values
    for (j = 0; j < h; j++) {
        for (i = 0; i < w; i++) {
            rgb1 = ((image[j][i][0] >> 5) << 6) | \
                   ((image[j][i][1] >> 5) << 3) | \
                    (image[j][i][2] >> 5);
            rgb2 = ((image[j+dy][i+dx][0] >> 5) << 6) | \
                   ((image[j+dy][i+dx][1] >> 5) << 3) | \
                    (image[j+dy][i+dx][2] >> 5);
            if (rgb1 < rgb2) temp = comatrix + (rgb2<<9) + rgb1;
            else             temp = comatrix + (rgb1<<9) + rgb2;
            if (*temp == 0) n++;
            (*temp)++;
        }
    }

    // Create the 1D array of indices and non-zero values in C on the heap
    index = 0;  // 1st half of array are row_column indices
    value = n;  // 2nd half of array are non-zero values
    n <<= 1;    // total array length consists from two halves
    if (!(arr = (unsigned int *) malloc(n * sizeof(unsigned int)))) return NULL;
    for (j = 0; j < 512; j++) {
        row = j << 9;  // 2^9 == 512
        for (i = 0; i <= j; i++) {
            k = *(comatrix + row + i);
            if (k) {
                arr[index] = row | i;  // row + i
                arr[value] = k;
                index++;
                value++;
            }
        }
    }

    // Return the array as a numpy array (numpy will free it later)
    dims1[0] = n;
    output = PyArray_SimpleNewFromData(1, dims1, NPY_UINT32, arr);
    // This is the critical line - tell numpy it has to free the data
    PyArray_ENABLEFLAGS((PyArrayObject*) output, NPY_ARRAY_OWNDATA);

    free(comatrix);  // free the memory of 2D array
    return output;
}

static PyObject *distance(PyObject *self, PyObject *args) {
    // Calculate distance between two descriptors and return it as an integer
    unsigned int dist = 0, index1 = 0, index2 = 0;
    unsigned int length1, length2, value1, value2, i1, i2;
    unsigned int *d1, *d2;  // two input arrays
    PyObject *input1 = NULL, *input2 = NULL;  // descriptor1 and descriptor2
    npy_intp dims1[1], dims2[1];  // 1D arrays
    PyArray_Descr *descr;

    // Expect two 1D arrays of descriptor values
    if (!PyArg_ParseTuple(args, "O!O!", &PyArray_Type, &input1,
                                        &PyArray_Type, &input2)) return NULL;

    // Create C arrays from numpy objects
    descr = PyArray_DescrFromType(NPY_UINT32);  // unsigned int
    if ((PyArray_AsCArray(&input1, (void *)&d1, dims1, 1, descr) < 0) ||
        (PyArray_AsCArray(&input2, (void *)&d2, dims2, 1, descr) < 0)) {
        PyErr_SetString(PyExc_TypeError, "error converting to c array");
        return NULL;
    }

    // Compare two descriptors and find a distance between them
    length1 = dims1[0] >> 1; value1 = length1; i1 = d1[index1];
    length2 = dims2[0] >> 1; value2 = length2; i2 = d2[index2];
    while (index1 < length1 && index2 < length2) {
        if (i1 < i2) {
            dist += d1[value1];
            index1++;
            value1++;
            i1 = d1[index1];
        } else if (i1 > i2) {
            dist += d2[value2];
            index2++;
            value2++;
            i2 = d2[index2];
        } else { // if (i1 == i2) -- rare event goes the last
            dist += abs((int)d1[value1] - (int)d2[value2]);
            index1++; index2++;
            value1++; value2++;
            i1 = d1[index1];
            i2 = d2[index2];
        }
    }
    while (index1 < length1) {  // finish 1st array
        dist += d1[value1];
        index1++;
        value1++;
    }
    while (index2 < length2) {  // finish 2nd array
        dist += d2[value2];
        index2++;
        value2++;
    }

    return Py_BuildValue("i", dist);
}
