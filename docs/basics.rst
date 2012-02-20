Basics
============

ws4py provides high-level, yet simple, interface to provide your application with WebSocket support.

.. code-block:: python

    from ws4py.websocket import WebSocket

The :class:`WebSocket <ws4py.websocket.WebSocket>` class should be sub-classed by your application to make something sensible with it. To the very least we suggest you override the :func:`received_message(message) <ws4py.websocket.WebSocket.received_message>` method.

For instance a straightforward echo application would look like this:

.. code-block:: python
    
    class EchoWebSocket(WebSocket):
        def received_message(self, message):
            self.send(message.data, message.is_binary)
        
Other useful methods to implement are:

   * :func:`opened() <ws4py.websocket.WebSocket.opened>` which is called whenever the WebSocket handshake is done.
   * :func:`closed(code, reason=None) <ws4py.websocket.WebSocket.closed>` which is called whenever the WebSocket connection is terminated.

You may want to know if the connection is currently usable or :attr:`terminated <ws4py.websocket.WebSocket.terminated>`.
