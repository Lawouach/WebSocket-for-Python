Basics
======

ws4py provides a high-level, yet simple, interface to provide your application with WebSocket support. It is simple as:

.. code-block:: python

    from ws4py.websocket import WebSocket

The :class:`WebSocket <ws4py.websocket.WebSocket>` class should be sub-classed by your application. To the very least we suggest you override the :func:`received_message(message) <ws4py.websocket.WebSocket.received_message>` method so that you can process incoming messages.

For instance a straightforward echo application would look like this:

.. code-block:: python

    class EchoWebSocket(WebSocket):
        def received_message(self, message):
            self.send(message.data, message.is_binary)

Other useful methods to implement are:

   * :func:`opened() <ws4py.websocket.WebSocket.opened>` which is called whenever the WebSocket handshake is done.
   * :func:`closed(code, reason=None) <ws4py.websocket.WebSocket.closed>` which is called whenever the WebSocket connection is terminated.

You may want to know if the connection is currently usable or :attr:`terminated <ws4py.websocket.WebSocket.terminated>`.

At that stage, the subclass is still not connected to any data source. The way ws4py is designed, you don't
necessarily a connected socket, in fact, you don't even need a socket at all.


.. code-block:: python

    >>> from ws4py.messaging import TextMessage
    >>> def data_source():
    >>>     yield TextMessage(u'hello world')

    >>> from mock import MagicMock
    >>> source = MagicMock(side_effect=data_source)
    >>> ws = EchoWebSocket(sock=source)
    >>> ws.send(u'hello there')
