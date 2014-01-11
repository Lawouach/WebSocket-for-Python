# -*- coding: utf-8 -*-
import base64
from hashlib import sha1
from email.parser import BytesHeaderParser
import io

import asyncio

from ws4py import WS_KEY, WS_VERSION
from ws4py.exc import HandshakeError
from ws4py.websocket import WebSocket

LF = b'\n'
CRLF = b'\r\n'
SPACE = b' '
EMPTY = b''

__all__ = ['WebSocketProtocol']

class WebSocketProtocol(asyncio.Protocol):
    def __init__(self, handler_cls):
        asyncio.Protocol.__init__(self)
        self.ws = handler_cls(self)
        
    def connection_made(self, transport):
        """
        A peer is now connected and we receive an instance
        of the underlying :class:`asyncio.Transport`.

        We :class:`asyncio.StreamReader` is created
        and the transport is associated before the
        initial HTTP handshake is undertaken.
        """
        self.transport = transport
        self.stream = asyncio.StreamReader()
        self.stream.set_transport(transport)
        asyncio.async(self.handle_initial_handshake())

    def close(self):
        """
        Initiate the websocket closing handshake
        which will eventuall lead to the underlying
        transport.
        """
        self.ws.close()
        
    def timeout(self):
        self.ws.close_connection()
        if self.ws.started:
            self.ws.closed(1002, "Peer connection timed-out")
        
    def connection_lost(self, exc):
        """
        The peer connection is now, the closing
        handshake won't work so let's not even try.
        However let's make the websocket handler
        be aware of it by calling its `closed`
        method.
        """
        self.ws.close_connection()
        if self.ws.started:
            self.ws.closed(1002, "Peer connection was lost")
            
    def data_received(self, data):
        self.stream.feed_data(data)

    @asyncio.coroutine
    def handle_initial_handshake(self):
        """
        Performs the HTTP handshake described in :rfc:`6455`. Note that
        this implementation is really basic and it is strongly advised
        against using it in production. It would probably break for
        most clients. If you want a better support for HTTP, please
        use a more reliable HTTP server implemented using asyncio.
        """
        request_line = yield from self.next_line()
        method, uri, req_protocol = request_line.strip().split(SPACE, 2)
        
        # GET required
        if method.upper() != b'GET':
            raise HandshakeError('HTTP method must be a GET')
        
        headers = yield from self.read_headers()
        
        for key, expected_value in [('Upgrade', 'websocket'),
                                     ('Connection', 'upgrade')]:
            actual_value = headers.get(key, '').lower()
            if not actual_value:
                raise HandshakeError('Header %s is not defined' % str(key))
            if expected_value not in actual_value:
                raise HandshakeError('Illegal value for header %s: %s' %
                                     (key, actual_value))

        response_headers = {}

        ws_version = WS_VERSION
        version = headers.get('Sec-WebSocket-Version')
        supported_versions = ', '.join([str(v) for v in ws_version])
        version_is_valid = False
        if version:
            try: version = int(version)
            except: pass
            else: version_is_valid = version in ws_version

        if not version_is_valid:
            response_headers['Sec-WebSocket-Version'] = supported_versions
            raise HandshakeError('Unhandled or missing WebSocket version')

        key = headers.get('Sec-WebSocket-Key')
        if key:
            ws_key = base64.b64decode(key.encode('utf-8'))
            if len(ws_key) != 16:
                raise HandshakeError("WebSocket key's length is invalid")

        protocols = []
        subprotocols = headers.get('Sec-WebSocket-Protocol')
        if subprotocols:
            ws_protocols = []
            for s in subprotocols.split(','):
                s = s.strip()
                if s in protocols:
                    ws_protocols.append(s)

        exts = []
        extensions = headers.get('Sec-WebSocket-Extensions')
        if extensions:
            for ext in extensions.split(','):
                ext = ext.strip()
                if ext in exts:
                    ws_extensions.append(ext)

        self.transport.write(('%s 101 Switching Protocols\r\n' % req_protocol).encode('utf-8'))
        self.transport.write(b'Upgrade: websocket\r\n')
        self.transport.write(b'Content-Length: 0\r\n')
        self.transport.write(b'Connection: Upgrade\r\n')
        self.transport.write(b'Sec-WebSocket-Version:' + bytes(str(version), 'utf-8') + CRLF)
        self.transport.write(b'Sec-WebSocket-Accept:' + base64.b64encode(sha1(key.encode('utf-8') + WS_KEY).digest()) + CRLF)
        self.transport.write(CRLF)

        yield from self.handle_websocket()

    @asyncio.coroutine
    def handle_websocket(self):
        """
        Starts the websocket process until the
        exchange is completed and terminated.
        """
        yield from self.ws.run()
        
    @asyncio.coroutine
    def read_headers(self):
        """
        Read all HTTP headers from the HTTP request
        and returns a dictionary of them.
        """
        headers = b''
        while True:
            line = yield from self.next_line()
            headers += line
            if line == CRLF:
                break
        return BytesHeaderParser().parsebytes(headers)
        
    @asyncio.coroutine
    def next_line(self):
        """
        Reads data until \r\n is met and then return all read
        bytes. 
        """
        line = yield from self.stream.readline()
        if not line.endswith(CRLF):
            raise ValueError("Missing mandatory trailing CRLF")
        return line
        
if __name__ == '__main__':
    from ws4py.websocket import AsyncEchoWebSocket
    
    loop = asyncio.get_event_loop()

    def start_server():
        proto_factory = lambda: WebSocketProtocol(AsyncEchoWebSocket)
        return loop.create_server(proto_factory, '', 7002)

    s = loop.run_until_complete(start_server())
    print('serving on', s.sockets[0].getsockname())
    loop.run_forever()
