# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()

import copy

import gevent
from gevent import Greenlet
from gevent.queue import Queue

from ws4py.client import WebSocketBaseClient

__all__ = ['WebSocketClient']

class WebSocketClient(WebSocketBaseClient):
    def __init__(self, url, protocols=None, extensions=None):
        WebSocketBaseClient.__init__(self, url, protocols, extensions)
        self._th = Greenlet(self.run)

        self.messages = Queue()

    def handshake_ok(self):
        self._th.start()

    def received_message(self, message):
        self.messages.put(copy.deepcopy(message))

    def closed(self, code, reason=None):
        # When the connection is closed, put a StopIteration
        # on the message queue to signal there's nothing left
        # to wait for
        self.messages.put(StopIteration)

    def receive(self):
        # If the websocket was terminated and there are no messages
        # left in the queue, return None immediately otherwise the client
        # will block forever
        if self.terminated and self.messages.empty():
            return None
        message = self.messages.get()
        if message is StopIteration:
            return None
        return message

if __name__ == '__main__':

    ws = WebSocketClient('http://localhost:9000/ws', protocols=['http-only', 'chat'])
    ws.connect()

    ws.send("Hello world")
    print((ws.receive(),))

    ws.send("Hello world again")
    print((ws.receive(),))

    def incoming():
        while True:
            m = ws.receive()
            if m is not None:
                print((m, len(str(m))))
                if len(str(m)) == 35:
                    ws.close()
                    break
            else:
                break
        print(("Connection closed!",))

    def outgoing():
        for i in range(0, 40, 5):
            ws.send("*" * i)

        # We won't get this back
        ws.send("Foobar")

    greenlets = [
        gevent.spawn(incoming),
        gevent.spawn(outgoing),
    ]
    gevent.joinall(greenlets)
