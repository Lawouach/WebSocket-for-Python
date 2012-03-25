# -*- coding: utf-8 -*-
import copy
import base64
from hashlib import sha1
import types
import socket

from ws4py import WS_KEY, WS_VERSION
from ws4py.exc import HandshakeError, StreamClosed
from ws4py.streaming import Stream
from ws4py.websocket import WebSocket

class WebSocketUpgradeMiddleware(object):
    def __init__(self, app, fallback_app=None, protocols=None, extensions=None,
                    websocket_class=WebSocket, versions=WS_VERSION):
        """
        WSGI middleware that performs the WebSocket upgrade handshake.

        .. code-block:: python
           :linenos:

           def ws_handler(websocket):
              ...

           app = WebSocketUpgradeMiddleware(ws_handler)
        

        If the handshake succeeds, it calls ``app`` with an instance of
        ``websocket_class`` with a copy of the environ dictionary.

        If an error occurs and ``fallback_app`` is provided, it must be a
        WSGI application which will be called. Otherwise it returns a
        simple error through the inner ``start_response``.

        One interesting aspect is that wsgiref fails with this middleware
        due to the ``Upgrade`` hop-by-hop header which is not allowed.

        Make sure that your server does not close the underlying socket for you
        since it would close the whole WebSocket connection as well.

        You may provide your own representation of the socket by setting
        the environ key: ``'upgrade.socket'``. Otherwise, ``'wsgi.input'._sock``
        will be used.
        """
        self.app = app
        self.fallback_app = fallback_app
        self.protocols = protocols
        self.extensions = extensions
        self.websocket_class = websocket_class
        self.versions = versions
        self.supported_versions = ', '.join([str(v) for v in versions])
    
    def __call__(self, environ, start_response):  
        # Initial handshake validation
        try:
            if 'websocket' not in environ.get('upgrade.protocol', environ.get('HTTP_UPGRADE', '')).lower():
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
            version_is_valid = False
            if version:
                try: version = int(version)
                except: pass
                else: version_is_valid = version in self.versions
                        
            if not version_is_valid:
                raise HandshakeError('Unsupported WebSocket version: %s' % version)

            environ['websocket.version'] = str(version)
        except HandshakeError, e:
            if self.fallback_app:
                return self.fallback_app(environ, start_response)
            else:
                start_response("400 Bad Handshake",
                               [('Sec-WebSocket-Version', self.supported_versions)])
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

        if 'upgrade.socket' in environ:
            upgrade_socket = environ['upgrade.socket']
        else:
            upgrade_socket = environ['wsgi.input']._sock
            
        return self.app(self.websocket_class(upgrade_socket,
                                             ws_protocols,
                                             ws_extensions,
                                             environ.copy()))
