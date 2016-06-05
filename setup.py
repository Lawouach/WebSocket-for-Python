# -*- coding: utf-8 -*-
import os, os.path
from glob import iglob
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from distutils.command.build_py import build_py

class buildfor2or3(build_py):
    def find_package_modules(self, package, package_dir):
        """
        Lookup modules to be built before install. Because we
        only use a single source distribution for Python 2 and 3,
        we want to avoid specific modules to be built and deployed
        on Python 2.x. By overriding this method, we filter out
        those modules before distutils process them.

        This is in reference to issue #123.
        """
        modules = build_py.find_package_modules(self, package, package_dir)
        amended_modules = []
        for (package_, module, module_file) in modules:
            if sys.version_info < (3,):
                if module in ['async_websocket', 'tulipserver']:
                    continue
            amended_modules.append((package_, module, module_file))
        return amended_modules
  
setup(name = "ws4py",
      version = '0.3.5',
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
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Communications',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      cmdclass=dict(build_py=buildfor2or3)
     )
