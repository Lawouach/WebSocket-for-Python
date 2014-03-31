# -*- coding: utf-8 -*-
import os, os.path
from glob import iglob
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from distutils.command.build_py import build_py

  
setup(name = "ws4py",
      version = '0.3.4',
      description = "WebSocket client and server library for Python 2 and 3 as well as PyPy",
      maintainer = "Sylvain Hellegouarch",
      maintainer_email = "sh@defuze.org",
      url = "https://github.com/Lawouach/WebSocket-for-Python",
      download_url = "https://pypi.python.org/pypi/ws4py",
      packages = ['ws4py', 'ws4py.client', 'ws4py.server'],
      platforms = ["any"],
      license = 'BSD',
      long_description = "WebSocket client and server library for Python 2 and 3 as well as PyPy",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
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
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ]
     )
