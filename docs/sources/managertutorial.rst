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

Client example
--------------

Below is a simple example on how to start 2000 clients against
a single server.

.. code-block:: python
    :linenos:

    from ws4py.client import WebSocketBaseClient
    from ws4py.manager import WebSocketManager
    from ws4py import format_addresses, configure_logger

    logger = configure_logger()

    m = WebSocketManager()

    class EchoClient(WebSocketBaseClient):
        def handshake_ok(self):
            logger.info("Opening %s" % format_addresses(self))
            m.add(self)

    	def received_message(self, msg):
            logger.info(str(msg))

    if __name__ == '__main__':
        import time
    
        try:
            m.start()
            for i in range(2000):
                client = EchoClient('ws://localhost:9000/ws')
                client.connect()

            logger.info("%d clients are connected" % i)

            while True:
                for ws in m.websockets.itervalues():
                    if not ws.terminated:
                       break
            	else:
                    break
            	time.sleep(3)
    	except KeyboardInterrupt:
            m.close_all()
            m.stop()
            m.join()

Once those are created against the ``echo_cherrypy_server`` example for instance,
point your browser to http://localhost:9000/ and enter a message. It will be
broadcasted to all connected peers.

When a peer is closed, its connection is automatically removed from the manager
so you should never need to explicitely remove it.

.. note::

   The CherryPy and wsgiref servers internally use a manager to handle connected
   websockets. The gevent server relies only on a greenlet 
   `group <http://www.gevent.org/gevent.pool.html#gevent.pool.Group>`_ instead.
