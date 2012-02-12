import copy
import base64
from hashlib import sha1
import types
import socket

import gevent
from gevent.coros import Semaphore as Lock
from gevent.queue import Queue

from ws4py import WS_KEY
from ws4py.exc import HandshakeError, StreamClosed
from ws4py.streaming import Stream
from ws4py.websocket import WebSocket

WS_VERSION = 13

class WebSocketUpgradeMiddleware(object):
    """WSGI middleware for handling WebSocket upgrades"""
    
    def __init__(self, fallback_app=None, protocols=None, extensions=None,
                    websocket_class=WebSocket):
        self.fallback_app = fallback_app
        self.protocols = protocols
        self.extensions = extensions
        self.websocket_class = websocket_class
    
    def __call__(self, environ, start_response):        
        # Initial handshake validation
        try:
            if 'websocket' not in environ.get('upgrade.protocol', '').lower():
                raise HandshakeError("Upgrade protocol is not websocket")
            
            if environ.get('REQUEST_METHOD') != 'GET':
                raise HandshakeError('Method is not GET')
            
            key = environ.get('HTTP_SEC_WEBSOCKET_KEY')
            if key:
                ws_key = base64.b64decode(key)
                if len(ws_key) != 16:
                    raise HandshakeError("WebSocket key's length is invalid")
            else:
                raise HandshakeError("Not a valid HyBi WebSocket request")
            
            version = environ.get('HTTP_SEC_WEBSOCKET_VERSION')
            if version:
                if version != str(WS_VERSION):
                    raise HandshakeError('Unsupported WebSocket version')
                environ['websocket.version'] = str(WS_VERSION)
            else:
                raise HandshakeError('WebSocket version required')
        except HandshakeError, e:
            if self.fallback_app:
                return self.fallback_app(environ, start_response)
            else:
                start_response("400 Bad Handshake", [])
                return [str(e)]
        
        # Collect supported subprotocols
        protocols = self.protocols or []
        subprotocols = environ.get('HTTP_SEC_WEBSOCKET_PROTOCOL')
        ws_protocols = []
        if subprotocols:
            for s in subprotocols.split(','):
                s = s.strip()
                if s in protocols:
                    ws_protocols.append(s)

        # Collect supported extensions
        exts = self.extensions or []
        ws_extensions = []
        extensions = environ.get('HTTP_SEC_WEBSOCKET_EXTENSIONS')
        if extensions:
            for ext in extensions.split(','):
                ext = ext.strip()
                if ext in exts:
                    ws_extensions.append(ext)
        
        # Build and start the HTTP response
        headers = [
            ('Upgrade', 'websocket'),
            ('Connection', 'Upgrade'),
            ('Sec-WebSocket-Version', environ['websocket.version']),
            ('Sec-WebSocket-Accept', base64.b64encode(sha1(key + WS_KEY).digest())),
        ]
        if ws_protocols:
            headers.append(('Sec-WebSocket-Protocol', ', '.join(ws_protocols)))
        if ws_extensions:
            headers.append(('Sec-WebSocket-Extensions', ','.join(ws_extensions)))
        
        start_response("101 Web Socket Hybi Handshake", headers)
        
        # Build a websocket object and pass it to the handler
        ws = self.websocket_class(environ.get('upgrade.socket'), 
                                  ws_protocols, 
                                  ws_extensions)
        ws.start()
        ws.join()
