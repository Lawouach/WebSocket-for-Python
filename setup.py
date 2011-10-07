# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name = "ws4py",
      version = '0.1.4',
      description = "WebSocket library for Python",
      maintainer = "Sylvain Hellegouarch",
      maintainer_email = "sh@defuze.org",
      url = "https://github.com/Lawouach/WebSocket-for-Python",
      download_url = "http://www.defuze.org/oss/ws4py/",
      packages = ["ws4py", "ws4py.client", "ws4py.server",
                  "ws4py.server.handler", "ws4py.server.wsgi"],
      platforms = ["any"],
      license = 'BSD',
      long_description = "WebSocket library for the Python",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: CherryPy',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Communications',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
          'Topic :: Software Development :: Libraries :: Python Modules'
          ],
     )
