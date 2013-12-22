Client
======

ws4py comes with various client implementations and they roughly share the same interface.


Built-in
--------

The built-in client relies only on modules provided by the Python stdlib. The
client's inner loop runs within a thread and therefore holds the thread alive
until the websocket is closed.

.. code-block:: python
    :linenos:

    from ws4py.client.threadedclient import WebSocketClient

    class DummyClient(WebSocketClient):
        def opened(self):
       	    def data_provider():
                for i in range(1, 200, 25):
                    yield "#" * i
                
            self.send(data_provider())

            for i in range(0, 200, 25):
                print i
            	self.send("*" * i)

        def closed(self, code, reason=None):
            print "Closed down", code, reason

        def received_message(self, m):
            print m
            if len(m) == 175:
                self.close(reason='Bye bye')

    if __name__ == '__main__':
        try:
            ws = DummyClient('ws://localhost:9000/', protocols=['http-only', 'chat'])
            ws.connect()
            ws.run_forever()
        except KeyboardInterrupt:
            ws.close()

In this snippet, when the handshake is successful, the :meth:`opened() <ws4py.websocket.WebSocket.opened>` method is called and within this method we immediately send a bunch of messages to the server. First we demonstrate how you can use a generator to do so, then we simply send strings.

Assuming the server echoes messages as they arrive, the :func:`received_message(message) <ws4py.websocket.WebSocket.received_message>` method will print out the messages returned by the server and simply close the connection once it receives the last sent messages, which length is 175.

Finally the :func:`closed(code, reason=None) <ws4py.websocket.WebSocket.closed>` method is called with the code and reason given by the server.

.. seealso::
   :ref:`manager`.

Tornado
-------

If you are using a Tornado backend you may use the Tornado client that ws4py provides as follow:


.. code-block:: python

    from ws4py.client.tornadoclient import TornadoWebSocketClient
    from tornado import ioloop

    class MyClient(TornadoWebSocketClient):
         def opened(self):
             for i in range(0, 200, 25):
                 self.send("*" * i)

         def received_message(self, m):
             print m
             if len(m) == 175:
                 self.close(reason='Bye bye')

         def closed(self, code, reason=None):
             ioloop.IOLoop.instance().stop()

    ws = MyClient('ws://localhost:9000/echo', protocols=['http-only', 'chat'])
    ws.connect()

    ioloop.IOLoop.instance().start()

gevent
------

If you are using a gevent backend you may use the gevent client that ws4py provides as follow:

.. code-block:: python

    from ws4py.client.geventclient import WebSocketClient

This client can benefit from gevent's concepts as demonstrated below:


.. code-block:: python

    ws = WebSocketClient('ws://localhost:9000/echo', protocols=['http-only', 'chat'])
    ws.connect()

    def incoming():
        """
	Greenlet waiting for incoming messages
	until ``None`` is received, indicating we can 
	leave the loop.
	"""
        while True:
            m = ws.receive()
            if m is not None:
               print str(m)
            else:
               break

    def send_a_bunch():
        for i in range(0, 40, 5):
           ws.send("*" * i)

    greenlets = [
        gevent.spawn(incoming),
        gevent.spawn(send_a_bunch),
    ]
    gevent.joinall(greenlets)

