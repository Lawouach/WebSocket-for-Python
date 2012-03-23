WebSocket for Python (ws4py)
============================

Python library providing an implementation of the WebSocket protocol defined in RFC 6455 (http://tools.ietf.org/html/rfc6455).

Overview
========

The latest stable release is 0.2.0. 

ws4py does not support older version of the protocol like Hixie-76.


Licensing
---------

ws4py is released under a BSD license.

Client support
--------------

To its simplest form, ws4py comes with a client that doesn't depends on anything but Python.
It's a threaded client as simple as:

```python
from ws4py.client.threadedclient import WebSocketClient
class EchoClient(WebSocketClient):
     def opened(self):
     	 print "Connection opened..."

     def closed(self, code, reason=None):
         print code, reason
            
     def received_message(self, m):
     	 self.send(m)

try:
    ws = EchoClient('http://localhost:9000/ws')
    ws.connect()
except KeyboardInterrupt:
    ws.close()
```

ws4py provides also a client based on Tornado and gevent. Strangely enough, Tornado
comes up with a server implementation but not a client. They work in a similar fashion.

Note that ws4py may should run on Android rather well through SL4A (http://code.google.com/p/android-scripting/).


Server support
--------------

ws4py does provides two server implementation. Mostly, servers are only used
for the initial HTTP handshake, once that's done ws4py takes over the socket
and the server isn't required any longer aside from managing the WebSocket instance
itself.

ws4py implements the server side through:

 * CherryPy
 * gevent

Tornado already offers its own implementation.

Getting Started
===============

Requirements
------------

As a standalone client, ws4py only requires Python 2.6.6 or above though it hasn't been ported to Python 3.x yet.

 * Tornado client requires Tornado 2.0.x (https://github.com/facebook/tornado)
 * CherryPy server requires CherryPy 3.2.2 (http://dowload.cherrypy.org/cherrypy/3.2.1/)
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

ws4py tries hard to be as conformant as it can to the specification. In order to validate this conformance, each release is run against the Autobahn testsuite (http://autobahn.ws/) which provides an extensive converage of various aspects of the protocol.

You will require the Autobahn test suite:

```
 $ pip install autobahntestsuite
```

In order to test the conformance of ws4py along other Python implementations, namely Autobahn 0.5+ and Tornado, run the followings:

```
 $ cd test
 $ python autobahn_test_servers.py --run-all
```

Next, run the Autobahn test suite from the ws4py test directory:

```
 $ wstest -m fuzzingclient -s fuzzingclient.json
```

Once the tests have finished, reports will be available from ```test/reports/servers```.

Online test reports can be found at: http://www.defuze.org/oss/ws4py/testreports/servers/

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