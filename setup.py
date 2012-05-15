# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name = "ws4py",
      version = '0.2.2',
      description = "WebSocket library for Python",
      maintainer = "Sylvain Hellegouarch",
      maintainer_email = "sh@defuze.org",
      url = "https://github.com/Lawouach/WebSocket-for-Python",
      download_url = "http://www.defuze.org/oss/ws4py/",
      packages = ["ws4py", "ws4py.client", "ws4py.server", "ws4py.server.wsgi"],
      tests_require=['unittest2', 'gevent', 'cherrypy'],
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
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Communications',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
          'Topic :: Software Development :: Libraries :: Python Modules'
          ],
     )
