# -*- coding: utf-8 -*-
from distutils.core import setup

setup(name = "ws4py",
      version = '0.1.2',
      description = "WebSocket library for Python",
      maintainer = "Sylvain Hellegouarch",
      maintainer_email = "sh@defuze.org",
      url = "https://github.com/Lawouach/WebSocket-for-Python",
      download_url = "http://www.defuze.org/oss/ws4py/",
      packages = ["ws4py", "ws4py.client", "ws4py.server", "ws4py.server.handler"],
      platforms = ["any"],
      license = 'BSD',
      long_description = "WebSocket library for the Python"
     )
