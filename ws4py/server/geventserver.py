# -*- coding: utf-8 -*-
__doc__ = """
WSGI entities to support WebSocket from within gevent.

Its usage is rather simple:

.. code-block: python

    from gevent import monkey; monkey.patch_all()
    from ws4py.websocket import EchoWebSocket
    from ws4py.server.geventserver import WSGIServer
    from ws4py.server.wsgiutils import WebSocketWSGIApplication

    server = WSGIServer(('localhost', 9000), WebSocketWSGIApplication(handler_cls=EchoWebSocket))
    server.serve_forever()

"""
import logging
import sys

import gevent
from gevent.pywsgi import WSGIHandler, WSGIServer as _WSGIServer
from gevent.pool import Group

from ws4py import format_addresses
from ws4py.server.wsgiutils import WebSocketWSGIApplication

logger = logging.getLogger('ws4py')

__all__ = ['WebSocketWSGIHandler', 'WSGIServer']

class WebSocketWSGIHandler(WSGIHandler):
    """
    A WSGI handler that will perform the :rfc:`6455`
    upgrade and handshake before calling the WSGI application.

    If the incoming request doesn't have a `'Upgrade'` header,
    the handler will simply fallback to the gevent builtin's handler
    and process it as per usual.
    """

    def run_application(self):
        upgrade_header = self.environ.get('HTTP_UPGRADE', '').lower()
        if upgrade_header:
            try:
                # Build and start the HTTP response
                self.environ['ws4py.socket'] = self.socket or self.environ['wsgi.input'].rfile._sock
                self.result = self.application(self.environ, self.start_response) or []
                self.process_result()
            except:
                raise
            else:
                del self.environ['ws4py.socket']
                self.socket = None
                self.rfile.close()

                ws = self.environ.pop('ws4py.websocket')
                if ws:
                    self.server.link_websocket_to_server(ws)
        else:
            gevent.pywsgi.WSGIHandler.run_application(self)

class WSGIServer(_WSGIServer):
    handler_class = WebSocketWSGIHandler

    def __init__(self, *args, **kwargs):
        """
        WSGI server that simply tracks websockets
        and send them a proper closing handshake
        when the server terminates.

        Other than that, the server is the same
        as its :class:`gevent.pywsgi.WSGIServer`
        base.
        """
        _WSGIServer.__init__(self, *args, **kwargs)
        self._websockets = Group()

    def link_websocket_to_server(self, websocket):
        logger.info("Managing websocket %s" % format_addresses(websocket))
        self._websockets.spawn(websocket.run)

    def stop(self, *args, **kwargs):
        logger.info("Terminating server and all connected websockets")
        for greenlet in self._websockets:
            try:
                websocket = greenlet._run.im_self
                if websocket:
                    websocket.close(1001, 'Server is shutting down')
            except:
                pass
        _WSGIServer.stop(self, *args, **kwargs)

if __name__ == '__main__':
    from ws4py import configure_logger
    configure_logger()

    from ws4py.websocket import EchoWebSocket
    server = WSGIServer(('127.0.0.1', 9000),
                        WebSocketWSGIApplication(handler_cls=EchoWebSocket))
    server.serve_forever()
