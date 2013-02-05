# -*- coding: utf-8 -*-
__doc__ = """
WSGI entities to support WebSocket from within gevent.

Its usage is rather simple:

    >>> from gevent import monkey; monkey.patch_all()
    >>> from ws4py.websocket import EchoWebSocket
    >>> from ws4py.server.geventserver import WebSocketWSGIApplication, WSGIServer

    >>> server = WSGIServer(('localhost', 9000), WebSocketWSGIApplication(handler_cls=EchoWebSocket))
    >>> server.serve_forever()

"""
import base64
from hashlib import sha1
import logging
import signal
import sys

import gevent
from gevent.pywsgi import WSGIHandler, WSGIServer as _WSGIServer
from gevent.pool import Group

from ws4py.websocket import WebSocket
from ws4py.exc import HandshakeError
from ws4py.compat import enc
from ws4py import WS_VERSION, WS_KEY, format_addresses

logger = logging.getLogger('ws4py')

__all__ = ['WebSocketWSGIHandler', 'WebSocketWSGIApplication', 'WSGIServer']

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
                # A couple of dummy validations
                if self.environ.get('REQUEST_METHOD') != 'GET':
                    raise HandshakeError('HTTP method must be a GET')

                for key, expected_value in [('HTTP_UPGRADE', 'webscket'),
                                            ('HTTP_CONNECTION', 'upgrade')]:
                    actual_value = self.environ.get(key, '').lower()
                    if not actual_value:
                        raise HandshakeError('Header %s is not defined' % key)
                    if expected_value not in actual_value:
                        raise HandshakeError('Illegal value for header %s: %s' %
                                             (key, actual_value))

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

                ws = self.environ.pop('ws4y.websocket')
                if ws:
                    self.server.link_websocket_to_server(ws)
        else:
            gevent.pywsgi.WSGIHandler.run_application(self)

class WebSocketWSGIApplication(object):
    def __init__(self, protocols=None, extensions=None,
                 version=WS_VERSION, handler_cls=WebSocket):
        """
        WSGI application usable to complete the upgrade handshake
        by validating the requested protocols and extensions as
        well as the websocket version.

        If the upgrade validates, the `handler_cls` class
        is instanciated and stored inside the WSGI `environ`
        under the `'ws4y.websocket'` key to make it
        available to the WSGI handler.

        Note that the key and its associated value will be removed
        from the environ dictionary from within the
        WSGI handler.
        """
        self.protocols = protocols
        self.extensions = extensions
        self.version = version
        self.handler_cls = handler_cls

    def build_websocket(self, sock, protocols, extensions, environ):
        """
        Initialize the `handler_cls` instance with the given
        negociated sets of protocols and extensions as well as
        the `environ` and `sock`.

        Stores then the instance in the `environ` dict
        under the `'ws4y.websocket'` key.
        """
        websocket = self.handler_cls(sock, protocols, extensions,
                                     environ.copy())
        environ['ws4y.websocket'] = websocket
        return websocket

    def __call__(self, environ, start_response):
        key = environ.get('HTTP_SEC_WEBSOCKET_KEY')
        if key:
            ws_key = base64.b64decode(enc(key))
            if len(ws_key) != 16:
                raise HandshakeError("WebSocket key's length is invalid")

        version = environ.get('HTTP_SEC_WEBSOCKET_VERSION')
        supported_versions = ', '.join([str(v) for v in self.version])
        version_is_valid = False
        if version:
            try: version = int(version)
            except: pass
            else: version_is_valid = version in WS_VERSION

        if not version_is_valid:
            environ['websocket.version'] = str(version)
            raise HandshakeError('Unhandled or missing WebSocket version')

        ws_protocols = []
        protocols = self.protocols or []
        subprotocols = environ.get('HTTP_SEC_WEBSOCKET_PROTOCOL')
        if subprotocols:
            for s in subprotocols.split(','):
                s = s.strip()
                if s in protocols:
                    ws_protocols.append(s)

        ws_extensions = []
        exts = self.extensions or []
        extensions = environ.get('HTTP_SEC_WEBSOCKET_EXTENSIONS')
        if extensions:
            for ext in extensions.split(','):
                ext = ext.strip()
                if ext in exts:
                    ws_extensions.append(ext)

        upgrade_headers = [
            ('Upgrade', 'websocket'),
            ('Connection', 'Upgrade'),
            ('Sec-WebSocket-Version', str(version)),
            ('Sec-WebSocket-Accept', base64.b64encode(sha1(key + WS_KEY).digest())),
            ]
        if ws_protocols:
            upgrade_headers.append(('Sec-WebSocket-Protocol', ', '.join(ws_protocols)))
        if ws_extensions:
            upgrade_headers.append(('Sec-WebSocket-Extensions', ','.join(ws_extensions)))

        start_response("101 Switching Protocols", upgrade_headers)

        self.build_websocket(environ['ws4py.socket'], ws_protocols,
                             ws_extensions, environ)

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
    server = WSGIServer(('127.0.0.1', 9001),
                        WebSocketWSGIApplication(handler_cls=EchoWebSocket))
    server.serve_forever()
