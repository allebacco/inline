
import inline
import sys
import os
import ctypes

code = r'''

#include <Python.h>

//#define API_EXPORT  __declspec(dllexport)
#define API_EXPORT

extern "C" API_EXPORT int add(int a, int b)
{
    return a + b;
}


extern "C" API_EXPORT PyObject* pyadd(PyObject* py_a, PyObject* py_b)
{
    int a = PyLong_AsLong(py_a);
    int b = PyLong_AsLong(py_b);

    return PyLong_FromLong(a + b);
}

int main()
{
    return 0;
}

'''

library_dir1 = os.path.join(sys.prefix, 'libs')
library_dir2 = os.path.join(sys.prefix, 'lib')
include_dir1 = os.path.join(sys.prefix, 'include')
include_dir2 = os.path.join(sys.prefix, 'include', 'python3.4')

include_dirs = [include_dir1, include_dir2]
lib_dirs = [library_dir1, library_dir2, sys.prefix]
adder = inline.cxx(code, libraries=['python3.4m'], include_dirs=include_dirs, lib_dirs=lib_dirs)

result = adder.add(40, 2)


adder.pyadd.restype = ctypes.py_object
adder.pyadd.argtypes = [ctypes.py_object, ctypes.py_object]

print('adder.pyadd', adder.pyadd)
print('args', adder.pyadd.argtypes)
print('return', adder.pyadd.restype)

pyadd = ctypes.PYFUNCTYPE(ctypes.py_object, ctypes.py_object, ctypes.py_object)(adder.pyadd)

print('Result is', result)
assert result == 40 + 2

pyresult = None
a = 30
b = 11
pyresult = pyadd(a, b)
print('Py Result is', pyresult)
