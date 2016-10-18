
import inline
import sys
import os
import ctypes

code = r'''

#include <python.h>

extern "C" __declspec(dllexport) int add(int a, int b)
{
    return a + b;
}


extern "C" __declspec(dllexport) PyObject* pyadd(PyObject* py_a, PyObject* py_b)
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

prefix = sys.prefix
library_dir = os.path.join(sys.prefix, 'libs')
include_dir = os.path.join(sys.prefix, 'include')
adder = inline.cxx(code, libraries=['python35'], include_dirs=[include_dir], lib_dirs=[library_dir, sys.prefix])

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
