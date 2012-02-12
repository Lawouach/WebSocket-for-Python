# -*- coding: utf-8 -*-
from base64 import b64encode, b64encode
from hashlib import sha1
import os
import types
from urlparse import urlsplit
import json

from ws4py import WS_KEY
from ws4py.streaming import Stream
from ws4py.exc import HandshakeError

__all__ = ['WebSocketBaseClient']

class WebSocketBaseClient(object):
    def __init__(self, url, protocols=None, version='13'):
        self.stream = Stream(always_mask=True, expect_masking=False)
        self.url = url
        self.protocols = protocols
        self.version = version
        self.key = b64encode(os.urandom(16))
        self.client_terminated = False
        self.server_terminated = False
        
    @property
    def handshake_headers(self):
        parts = urlsplit(self.url)
        host = parts.netloc
        if ':' in host:
            host, port = parts.netloc.split(':')
            
        headers = [
            ('Host', host),
            ('Connection', 'Upgrade'),
            ('Upgrade', 'websocket'),
            ('Sec-WebSocket-Key', self.key),
            ('Sec-WebSocket-Origin', self.url),
            ('Sec-WebSocket-Version', self.version)
            ]
        
        if self.protocols:
            headers.append(('Sec-WebSocket-Protocol', ','.join(self.protocols)))

        return headers

    @property
    def handshake_request(self):
        parts = urlsplit(self.url)
        
        headers = self.handshake_headers
        request = ["GET %s HTTP/1.1" % parts.path]
        for header, value in headers:
            request.append("%s: %s" % (header, value))
        request.append('\r\n')

        return '\r\n'.join(request)

    def process_response_line(self, response_line):
        protocol, code, status = response_line.split(' ', 2)
        if code != '101':
            raise HandshakeError("Invalid response status: %s %s" % (code, status))

    def process_handshake_header(self, headers):
        protocols = []
        extensions = []

        headers = headers.strip()
        
        for header_line in headers.split('\r\n'):
            header, value = header_line.split(':', 1)
            header = header.strip().lower()
            value = value.strip().lower()
            
            if header == 'upgrade' and value != 'websocket':
                raise HandshakeError("Invalid Upgrade header: %s" % value)

            elif header == 'connection' and value != 'upgrade':
                raise HandshakeError("Invalid Connection header: %s" % value)

            elif header == 'sec-websocket-accept':
                match = b64encode(sha1(self.key + WS_KEY).digest())
                if value != match.lower():
                    raise HandshakeError("Invalid challenge response: %s" % value)

            elif header == 'sec-websocket-protocol':
                protocols = ','.join(value)

            elif header == 'sec-websocket-extensions':
                extensions = ','.join(value)

        return protocols, extensions

    def opened(self, protocols, extensions):
        pass

    def received_message(self, m):
        pass

    def closed(self, code, reason=None):
        pass

    @property
    def terminated(self):
        return self.client_terminated is True and self.server_terminated is True
    
    def close(self, reason='', code=1000):
        if not self.client_terminated:
            self.client_terminated = True
            self.write_to_connection(self.stream.close(code=code, reason=reason).single(mask=True))

    def connect(self):
        raise NotImplemented()

    def write_to_connection(self, bytes):
        raise NotImplemented()

    def read_from_connection(self, amount):
        raise NotImplemented()

    def close_connection(self):
        raise NotImplemented()
               
    def send(self, payload, binary=False):
        message_sender = self.stream.binary_message if binary else self.stream.text_message
        
        if isinstance(payload, basestring):
            self.write_to_connection(message_sender(payload).single(mask=True))
        
        elif isinstance(payload, dict):
            self.write_to_connection(message_sender(json.dumps(payload)).single(mask=True))
        
        elif type(payload) == types.GeneratorType:
            first = True
            last = False
            bytes = payload.next()
            
            while not last:
                try:
                    peeked_bytes = payload.next()
                except StopIteration:
                    last = True
                    
                self.write_to_connection(message_sender(bytes).fragment(first=first, last=last, mask=True))
                first = False
                bytes = peeked_bytes

