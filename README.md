WebSocket for Python (ws4py)
============================

Python library providing support for the WebSocket protocol defined in RFC 6455 (http://tools.ietf.org/html/rfc6455).


Getting Started
===============

Requirements
------------

As a standalone client, ws4py only requires Python 2.6.6 or above though it hasn't been ported to Python 3.x yet.

 * Tornado client requires Tornado 2.0.x (https://github.com/facebook/tornado)
 * CherryPy server requires CherryPy 3.2.1 (http://dowload.cherrypy.org/cherrypy/3.2.1/)
 * gevent server requires gevent gevent 0.13.6 and 1.0.0dev (http://pypi.python.org/pypi/gevent/0.13.6)


Installing
----------

In order to install ws4py you can either grab the source code and run:

```
 $ python setup.py install
```

Or use a package manager like pip and run:

```
 $ pip install git+git://github.com/Lawouach/WebSocket-for-Python.git
```

Documentation
-------------

Online documentation can be found at: http://www.defuze.org/oss/ws4py/docs/

Conformance
-----------

ws4py tries hard to be as conformant as it can to the specification. In order to validate this conformance, each release is run against the Autobahn testsuite (http://www.tavendo.de/autobahn) which provides an extensive converage of various aspects of the protocol.

You may try to run it against the CherryPy server as follow:

```
 $ python test/autobahn_test_servers.py
```

Then from a different terminal:

```
 $ cd Autobahn/testsuite/websockets
 $ python fuzzing_client.py
```

This will run the complete suite. 

Test reports can be found at: http://www.defuze.org/oss/ws4py/testreports/servers/

Examples
--------

ws4py comes with a few examples:

 * The echo_cherrypy_server provides a simple Echo server. It requires CherryPy 3.2.2. Once started, you can point your browser (it has been tested with Chrome 15.0.854.0).
   Open a couple of tabs pointing at http://localhost:9000 and chat accross those tables.
 * The droid_sensor_cherrypy_server broadcasts sensor metrics to clients. Point your browser to http://localhost:9000
   Then run the droid_sensor module from your Android device using SL4A.
   A screenshot of what this renders to: http://www.defuze.org/oss/ws4py/screenshots/droidsensors.png

Credits
-------

Many thanks to the pywebsocket and Tornado projects which have provided a good base to write ws4py.
Thanks also to Jeff Lindsay (progrium) for the gevent server support.
A well deserved thank you to Tobias Oberstein for his websocket test suite: https://github.com/oberstet/Autobahn

The background in the droid example is courtesy of http://killxthexscenexstock.deviantart.com/art/Vintage-Wall-Paper-Texture-70982719