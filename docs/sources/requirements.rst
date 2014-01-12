.. _requirements:

Requirements
============

Python
------

Tested environments:

- Python 2.7+
- Python 3.3+
- PyPy 1.8+
- Android 2.3 via `SL4A <http://code.google.com/p/android-scripting/>`_

.. note::

   ws4py will not try to automatically install dependencies and will
   let you decide which one you need.

Client
------

ws4py comes with three client implementations:

- Built-in: That client is solely based on the Python stdlib, it uses a thread to run the inner processing loop.
- Tornado: The Tornado client requires `Tornado <http://www.tornadoweb.org>`_ 2.0+ 
- gevent: The gevent client requires `gevent <http://www.gevent.org/>`_ 0.13.6 or 1.0.0-dev 

Server
------

ws4py comes with three server implementations:

- Built-in: The server relies on the built-in :mod:`wsgiref` module.
- CherryPy: The `CherryPy <http://www.cherrypy.org/CherryPy>`_ server requires 3.2.2+
- gevent: The gevent server requires `gevent <http://www.gevent.org/>`_ 1.0.0
- asyncio: :pep:`3156` implementation for Python 3.3+

Testing
-------

ws4py uses the Autobahn functional test suite to ensure it respects the standard. You
must install it to run that test suite against ws4py.

- Autobahn `python <http://autobahn.ws/python>`_
- Autobahn `test suite <http://autobahn.ws/testsuite>`_ 
