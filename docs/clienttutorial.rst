Client
======

Built-in
--------

ws4py comes with various client implementation but they roughly share the same aspects when your application needs one.

An example is better than any word so let's have a look at a basic client:

.. code-block:: python

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

        def closed(self, code, reason):
            print "Closed down", code, reason

        def received_message(self, m):
            print "=> %d %s" % (len(m), str(m))
            if len(str(m)) == 175:
                self.close(reason='Bye bye')

    if __name__ == '__main__':
        try:
            ws = DummyClient('ws://localhost:9000/', protocols=['http-only', 'chat'])
            ws.connect()
        except KeyboardInterrupt:
            ws.close()

This example demonstrates how to implement a client, here based on a thread-model, that is able to send and receive messages from a connected endpoint at ws://localhost:9000/.

In this snippet, when the handshake is successful, the :func:`opened() <ws4py.websocket.WebSocket.opened>` method is called and within this method we immediatly send to the server a bunch of messages. First we demonstrate how you can use a generator to do so, then we simply send strings.

Assuming the server echoes messages as they arrive, the :func:`received_message(message) <ws4py.websocket.WebSocket.received_message>` method will print out the messages returned by the server and simply closes the connection once it receives the last sent messages , which length is 175.

Finally the :func:`closed(code, reason=None) <ws4py.websocket.WebSocket.closed>` method is called with the code and reason given by the server.

Tornado
-------

If you are using a Tornado backend you may use the Tornado client that ws4py provides as follow:


.. code-block:: python

    from ws4py.client.tornadoclient import WebSocketClient

The previous example runs exactly in the same way.


gevent
------

If you are using a gevent backend you may use the gevent client that ws4py provides as follow:


.. code-block:: python

    from ws4py.client.geventclient import WebSocketClient

The previous example runs exactly in the same way.

