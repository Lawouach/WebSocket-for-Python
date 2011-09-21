# -*- coding: utf-8 -*-
from urlparse import urlsplit
import copy

import gevent
from gevent import Greenlet
from gevent import socket
from gevent.coros import Semaphore
from gevent.queue import Queue

from ws4py.client.threadedclient import WebSocketClient as ThreadedClient
from ws4py.exc import HandshakeError, StreamClosed

__all__ = ['WebSocketClient']

class WebSocketClient(ThreadedClient):
    def __init__(self, url, protocols=None, version='8'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        ThreadedClient.__init__(self, url, protocols=protocols, version=version, sock=sock)
        
        self._lock = Semaphore()
        self._th = Greenlet(self._receive)
        self._messages = Queue()
        
        self.extensions = []

    def opened(self, protocols, extensions):
        self.protocols = protocols
        self.extensions = extensions
    
    def received_message(self, m):
        self._messages.put(copy.deepcopy(m))
    
    def write_to_connection(self, bytes):
        if not self.client_terminated:
            return self.sock.sendall(bytes)    
    
    def closed(self, code, reason=None):
        self._messages.put(StreamClosed(code, reason))
    
    def receive(self, msg_obj=False):
        msg = self._messages.get()
        
        if isinstance(msg, StreamClosed):
            return None
            
        if msg_obj:
            return msg
        else:
            return msg.data


if __name__ == '__main__':
                
    ws = WebSocketClient('http://localhost:9000/', protocols=['http-only', 'chat'])
    ws.connect()
    
    ws.send("Hello world")
    print ws.receive()
    
    ws.send("Hello world again")
    print ws.receive()
    
    def incoming():
        while True:
            m = ws.receive()
            if m is not None:
                print m, len(str(m))
                if len(str(m)) == 35:
                    ws.close()
                    break
            else:
                break
        print "Connection closed!"
    
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
