# -*- coding: utf-8 -*-
import os, os.path
from glob import iglob
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def gather_modules():
    """
    Lists all Python modules of the ws4py package.
    I wish there was a simpler way but because some
    modules use the 'yield from' statement, we
    can't simply pass a list of directories to setup
    below. Indeed, that would fail to compile
    those modules when running Python 2. At the same
    time, the MANIFEST doesn't work for bdist commands,
    only source distributions. Distutils is beyond
    annoying at cryptic at times. If you have a cleaner
    way, please do submit a patch as I'd love seeing it.
    """
    pjoin = os.path.join

    mods = []
    for root, dirs, files in os.walk('ws4py'):
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        
        for name in files:
            if name.endswith('.py'):
                mods.append(pjoin(root, name).replace('.py', ''))

    if sys.version_info < (3, 0):
        mods.remove(pjoin('ws4py', 'async_websocket.py').replace('.py', ''))
        mods.remove(pjoin('ws4py', 'server', 'tulipserver.py').replace('.py', ''))

    return mods

setup(name = "ws4py",
      version = '0.3.3',
      description = "WebSocket library for Python",
      maintainer = "Sylvain Hellegouarch",
      maintainer_email = "sh@defuze.org",
      url = "https://github.com/Lawouach/WebSocket-for-Python",
      download_url = "http://www.defuze.org/oss/ws4py/",
      py_modules=gather_modules(),
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
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Communications',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
          'Topic :: Software Development :: Libraries :: Python Modules'
          ],
     )
