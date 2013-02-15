# -*- coding: utf-8 -*-
import os
import sys
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

from distutils.command.build_ext import build_ext
from distutils.command.sdist import sdist

try:
    import Cython.Compiler.Main as cython_compiler
    have_cython = True
except ImportError:
    have_cython = False


class NoCython(Exception):
    pass

def cythonize(src):
    sys.stderr.write("cythonize: %r\n" % (src,))
    cython_compiler.compile([src])

def ensure_source(src):
    pyx = os.path.splitext(src)[0] + '.pyx'

    if not os.path.exists(src):
        if not have_cython:
            raise NoCython
        cythonize(pyx)
    elif (os.path.exists(pyx) and
          os.stat(src).st_mtime < os.stat(pyx).st_mtime and
          have_cython):
        cythonize(pyx)
    return src


class BuildExt(build_ext):
    def build_extension(self, ext):
        try:
            ext.sources = list(map(ensure_source, ext.sources))
        except NoCython:
            print("WARNING")
            print("Cython is required for building extension from checkout.")
            print("Install Cython >= 0.16 or install ws4py from PyPI.")
            print("Falling back to pure Python implementation.")
            return
        try:
            return build_ext.build_extension(self, ext)
        except Exception as e:
            print("WARNING: Failed to compile extensiom modules.")
            print("ws4py uses fallback pure python implementation.")
            print(e)


# take care of extension modules.
if have_cython:
    class Sdist(sdist):
        def __init__(self, *args, **kwargs):
            from glob import glob
            for src in glob('ws4py/*.pyx'):
                cythonize(src)
            sdist.__init__(self, *args, **kwargs)
else:
    Sdist = sdist

ext_modules = [
    Extension('ws4py.utf8validator_c', ['ws4py/utf8validator_c.c']),
    ]

test_require = ['unittest2', 'cherrypy']
if sys.version_info < (3, 0):
    test_require.append('gevent')

setup(name = "ws4py",
      version = '0.3.0-beta',
      description = "WebSocket library for Python",
      maintainer = "Sylvain Hellegouarch",
      maintainer_email = "sh@defuze.org",
      url = "https://github.com/Lawouach/WebSocket-for-Python",
      download_url = "http://www.defuze.org/oss/ws4py/",
      packages = ["ws4py", "ws4py.client", "ws4py.server"],
      cmdclass={'build_ext': BuildExt, 'sdist': Sdist},
      ext_modules=ext_modules,
      tests_require=test_require,
      test_suite='unittest2.collector',
      platforms = ["any"],
      license = 'BSD',
      long_description = "WebSocket library for Python",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: CherryPy',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Communications',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
          'Topic :: Software Development :: Libraries :: Python Modules'
          ],
     )
