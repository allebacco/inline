#!/usr/bin/env python
# -*- coding:utf-8 -*-

import atexit
import ctypes
import distutils.ccompiler
import os.path
import os
import platform
import shutil
import sys
import tempfile
import stat


__version__ = '0.0.1'


def c(source, libraries=[], include_dirs=None, lib_dirs=None):
    """
    >>> c('int add(int a, int b) {return a + b;}').add(40, 2)
    42
    >>> sqrt = c('''
    ... #include <math.h>
    ... double _sqrt(double x) {return sqrt(x);}
    ... ''', ['m'])._sqrt
    >>> sqrt.restype = ctypes.c_double
    >>> sqrt(ctypes.c_double(400.0))
    20.0
    """
    path = _cc_build_shared_lib(source, '.c', libraries, include_dirs, lib_dirs)
    return ctypes.cdll.LoadLibrary(path)


def cxx(source, libraries=[], include_dirs=None, lib_dirs=None):
    """
    >>> cxx('extern "C" { int add(int a, int b) {return a + b;} }').add(40, 2)
    42
    """
    path = _cc_build_shared_lib(source, '.cpp', libraries, include_dirs, lib_dirs)
    return ctypes.pydll.LoadLibrary(path)

cpp = cxx  # alias


def python(source):
    """
    >>> python('def add(a, b): return a + b').add(40, 2)
    42
    """
    obj = type('', (object,), {})()
    _exec(source, obj.__dict__, obj.__dict__)
    return obj


def _cc_build_shared_lib(source, suffix, libraries, include_dirs=None, lib_dirs=None):
    tempdir = tempfile.mkdtemp(prefix='inline_')
    print('Creating temp dir', tempdir)
    #atexit.register(lambda: shutil.rmtree(tempdir))
    cc = distutils.ccompiler.new_compiler()
    temp_file = tempfile.NamedTemporaryFile('w+', suffix=suffix, dir=tempdir, delete=False)
    temp_file.write(source)
    temp_filename_cpp = temp_file.name
    temp_file.close()
    assert os.path.exists(temp_filename_cpp)
    os.chmod(temp_filename_cpp, stat.S_IWRITE | stat.S_IREAD)
    args = []
    if platform.system() == 'Linux':
        args.append('-fPIC')
    elif platform.system() == 'Windows':
        args.append('/LD')
    objs = cc.compile([temp_filename_cpp], tempdir, extra_postargs=args, include_dirs=include_dirs)
    #for library in libraries:
    #    cc.add_library(library)
    cc.link_shared_lib(objs, temp_filename_cpp, output_dir=tempdir, libraries=libraries, library_dirs=lib_dirs)
    filename = cc.library_filename(temp_filename_cpp, 'shared')
    return os.path.join(tempdir, filename)


def _exec(object, globals, locals):
    r"""
    >>> d = {}
    >>> exec('a = 0', d, d)
    >>> d['a']
    0
    """
    if sys.version_info < (3,):
        exec('exec object in globals, locals')
    else:
        exec(object, globals, locals)
