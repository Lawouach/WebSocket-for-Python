# -*- coding: utf-8 -*-
import logging

from gevent import monkey; monkey.patch_all()
import gevent
from ws4py.server.geventserver import WebSocketWSGIApplication, \
     WebSocketWSGIHandler, GEventWebSocketPool
from ws4py.websocket import EchoWebSocket

from chaussette.backend._gevent import Server as GeventServer

class ws4pyServer(GeventServer):
    handler_class = WebSocketWSGIHandler

    def __init__(self, *args, **kwargs):
        GeventServer.__init__(self, *args, **kwargs)
        self.pool = GEventWebSocketPool()

    def stop(self, *args, **kwargs):
        self.pool.clear()
        self.pool = None
        GeventServer.stop(self, *args, **kwargs)

if __name__ == '__main__':
    import os, socket, sys
    from ws4py import configure_logger
    logger = configure_logger()

    from chaussette.backend import register
    register('ws4py', ws4pyServer)

    from chaussette.server import make_server
    server = make_server(app=WebSocketWSGIApplication(handler_cls=EchoWebSocket),
                         host='unix:///%s/ws.sock' % os.getcwd(),
                         address_family=socket.AF_UNIX,
                         backend='ws4py',
                         logger=logger)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
