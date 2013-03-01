WebSocket for Python (ws4py)
============================

[![Build Status](https://travis-ci.org/Lawouach/WebSocket-for-Python.png)](https://travis-ci.org/Lawouach/WebSocket-for-Python)

Python library providing an implementation of the WebSocket protocol defined in RFC 6455 (http://tools.ietf.org/html/rfc6455).

Overview
========

The latest stable release is 0.2.4.

The current development version is 0.3.0-beta.

ws4py does not support older version of the protocol like Hixie-76.


Licensing
---------

ws4py is released under a BSD license.

Platforms
---------

ws4py runs on:

 * CPython 2.6+/2.7+/3.2+
 * pypy 1.8/1.9

Implementation
--------------

ws4py data model is rather simple and follows the protocol itself:

 * a highlevel WebSocket class that determines actions to carry based on messages that are parsed.
 * a Stream class that handles a single message at a time
 * a Frame class that performs the low level protocol parsing of frames

Each are inter-connected as russian dolls generators. The process heavily relies on the
capacity to send to a generator. So everytime one of those layers requires something,
it yields and then its holder sends it back whatever was required.

The Frame parser yields the number of bytes it needs at any time, the stream parser
forwards it back to the WebSocket class which gets data from the underlying data provider
it holds a reference to (a socket typically). The WebSocket class sends bytes as they are read from the socket
down to the stream parser which forwards them to the frame parser.

Eventually a frame is parsed and handled by the stream parser which in turns
yields a complete message made of all parsed frames.

The interesting aspect here is that the socket provider is totally abstracted
from the protocol implementation which simply requires bytes as they come.

This means one could write a ws4py socket provider that doesn't read from the
wire but from any other source.

It's also pretty fast and easy to read.

Performance
-----------

ws4py doesn't perform too bad but it's far from being the fastest WebSocket lib under heavy load.
The reason is that it was first designed to implement the protocol with simplicity
and clarity in mind. Future developments will look at performances.

Note however that ws4py runs way faster with CherryPy on PyPy than it does on CPython.
And [wsaccel](https://github.com/methane/wsaccel) replaces some bottleneck with Cython implementation for CPython.

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
    ws = EchoClient('ws://localhost:9000/ws')
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

 * CherryPy (works with CPython 2.6+ and 3.2+ as well as PyPy)
 * gevent (works with CPython 2.6+)
 * wsgiref

Tornado already offers its own implementation.

Getting Started
===============

Requirements
------------

As a standalone client, ws4py only requires Python (2.6+ or 3.x).

 * Tornado client requires Tornado 2.0.x (https://github.com/facebook/tornado)
 * CherryPy server requires CherryPy 3.2.2 (http://dowload.cherrypy.org/cherrypy/3.2.2/)
 * gevent server requires gevent gevent 0.13.6 and 1.0.0dev (http://pypi.python.org/pypi/gevent/0.13.6)
 * SL4A for Android support (http://code.google.com/p/android-scripting/)

Since not everyone will want all of them, ws4py will not attempt to install them automatically.

Installing
----------

In order to install ws4py you can either grab the source code and run:

```
 $ python setup.py install
```

Or use a package manager like pip and run:

```
 $ pip install ws4py
```

or even:

```
 $ pip install git+git://github.com/Lawouach/WebSocket-for-Python.git
```

Documentation
-------------

Online documentation can be found at: https://ws4py.readthedocs.org/en/latest/

Continuous Build
----------------

Travis is running continuous building against the master branch at:

https://travis-ci.org/#!/Lawouach/WebSocket-for-Python

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

Browser Support
---------------

ws4py has been tested using:

 * Chromium 22
 * Firefox 16

Since Safari, Opera and IE do not yet support the protocol or the RFC's version, ws4py won't
work with them. See http://caniuse.com/websockets for reference.

Bear in mind that time is a premium and maintaining obsolete and unsecure protocols is not
one of ws4py's goals. It's therefore unlikely it will ever support them.

Examples
--------

ws4py comes with a few examples:

 * The ```echo_cherrypy_server``` example provides a simple Echo server. It requires CherryPy 3.2.2.
   Open a couple of tabs pointing at http://localhost:9000 and chat accross those tables.
 * The ```droid_sensor_cherrypy_server``` broadcasts sensor metrics to clients. Point your browser to http://localhost:9000
   Then run the ```droid_sensor``` module from your Android device using SL4A.
   A screenshot of what this renders to: http://www.defuze.org/oss/ws4py/screenshots/droidsensors.png

Credits
-------

Many thanks to the pywebsocket and Tornado projects which have provided a good base to write ws4py.
Thanks also to Jeff Lindsay (progrium) for the gevent server support.
A well deserved thank you to Tobias Oberstein for his websocket test suite: https://github.com/oberstet/Autobahn
