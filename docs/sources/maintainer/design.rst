.. _design:

Design
======

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


