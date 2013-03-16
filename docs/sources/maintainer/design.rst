.. _design:

Design
======

Workflow
--------

ws4py's design is actually fairly simple and straigtforward. At a high level this is what is going on:

.. seqdiag::

   seqdiag {
      === HTTP Upgrade exchange ===
      client -> webserver [label = "GET /ws"];
      client <-  webserver [label = "101 Switching Protocols"];
      === WebSocket exchange ===
      webserver --> ws4py_manager;
      ws4py_manager --> ws4py_websocket [label = "opened"];
      ws4py_manager --> ws4py_manager [label = "poll"];
      client -> ws4py_manager [label = "send"];
      ws4py_manager --> ws4py_websocket [label = "received"];
      client <- ws4py_websocket [label = "send"];
      ws4py_manager --> ws4py_manager [label = "poll"];
      client <- ws4py_websocket [label = "send"];
      === WebSocket closing exchange (client initiated) ===
      client -> ws4py_manager [label = "close"];
      ws4py_manager --> ws4py_websocket [label = "close"];
      client <- ws4py_websocket [label = "close"];
      ws4py_manager --> ws4py_manager [label = "poll"];
      ws4py_manager --> ws4py_websocket [label = "closed"];
   }

The initial connection is made by a WebSocket aware client to a WebSocket aware web server. The first exchange
is dedicated to perform the upgrade handshake as defined by :rfc:`6455#section-4`.

If the exchange succeeds, the socket is kept opened, wrapped into a :class:`ws4py.websocket.WebSocket` instance 
which is passed on to the global ws4py :class:`ws4py.manager.WebSocketManager` instance which will handle its lifecycle.

Most notably, the manager will poll for the socket's receive events so that, when bytes are available,
the websocket object can read and process them.

Implementation
--------------

ws4py data model is rather simple and follows the protocol itself:

- a highlevel :class:`ws4py.websocket.WebSocket` class that determines actions to carry based on messages that are parsed.
- a :class:`ws4py.streaming.Stream` class that handles a single message at a time
- a :class:`ws4py.framing.Frame` class that performs the low level protocol parsing of frames

Each are inter-connected as russian dolls generators. The process heavily relies on the capacity to send to a generator. So everytime one of those layers requires something, it yields and then its holder sends it back whatever was required.

The Frame parser yields the number of bytes it needs at any time, the stream parser forwards it back to the WebSocket class which gets data from the underlying data provider it holds a reference to (a socket typically). The WebSocket class sends bytes as they are read from the socket down to the stream parser which forwards them to the frame parser.

Eventually a frame is parsed and handled by the stream parser which in turns yields a complete message made of all parsed frames.

The interesting aspect here is that the socket provider is totally abstracted from the protocol implementation which simply requires bytes as they come.

This means one could write a ws4py socket provider that doesn't read from the wire but from any other source.

It's also pretty fast and easy to read.
