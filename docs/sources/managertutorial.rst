.. _manager:

Managing a pool of WebSockets
=============================

ws4py provides a :class:`ws4py.manager.WebSocketManager` class that takes care of 
:class:`ws4py.websocket.WebSocket` instances once they the HTTP upgrade handshake
has been performed.

The manager is not compulsory but makes it simpler to track and let them run
in your application's process.

When you :meth:`add(websocket) <ws4py.manager.WebSocketManager.add>` a 
websocket to the manager, the file-descriptor is registered with the 
manager's poller and the :meth:`opened() <ws4py.websocket.WebSocket.opened>` 
method on is called.

Polling
-------

The manager uses a polling mechanism to dispatch on socket incoming events.
Two pollers are implemented, one using the traditionnal :py:mod:`select` 
and another one based on `select.epoll <http://docs.python.org/2.7/library/select.html#epoll-objects>`_ 
which is used only if available on the system.

The polling is executed in its own thread, it keeps looping until
the manager :meth:`stop() <ws4py.websocket.WebSocket.stop>` method.

On every loop, the poller is called to poll for all registered file-descriptors.
If any one of them is ready, we retrieve the websocket using that descriptor
and, if the websocket is not yet terminated, we call its `once` method
so that the incoming bytes are processed.

If the processing fails in anyway, the manager terminates the websocket and
remove it from itself. 
