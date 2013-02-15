# -*- coding: utf-8 -*-
from base64 import b64encode
from hashlib import sha1
import os
import socket
import ssl

from ws4py import WS_KEY, WS_VERSION
from ws4py.exc import HandshakeError
from ws4py.websocket import WebSocket
from ws4py.compat import urlsplit, enc, dec

__all__ = ['WebSocketBaseClient']

class WebSocketBaseClient(WebSocket):
    def __init__(self, url, protocols=None, extensions=None, heartbeat_freq=None):
        """
        A websocket client that implements :rfc:`6455` and provides a simple
        interface to communicate with a websocket server.

        This class works on its own but will block if not run in
        its own thread.

        When an instance of this class is created, a :py:mod:`socket`
        is created with the nagle's algorithm disabled and with
        the capacity to reuse a port that was just used.

        The address of the server will be extracted from the given
        websocket url.

        The websocket key is randomly generated, reset the
        `key` attribute if you want to provide yours.

        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        WebSocket.__init__(self, sock, protocols=protocols,
                           extensions=extensions,
                           heartbeat_freq=heartbeat_freq)
        self.stream.always_mask = True
        self.stream.expect_masking = False
        self.key = b64encode(os.urandom(16))
        self.url = url

        self.host = None
        self.scheme = None
        self.port = None
        self.resource = None

        self._parse_url()

    # Adpated from: https://github.com/liris/websocket-client/blob/master/websocket.py#L105
    def _parse_url(self):
        if ":" not in self.url:
            raise ValueError("Invalid URL: %s" % self.url)

        # Python 2.6.1 and below don't parse ws or wss urls properly. netloc is empty.
        # See: https://github.com/Lawouach/WebSocket-for-Python/issues/59
        scheme, url = self.url.split(":", 1)

        parsed = urlsplit(url, scheme="http")
        if parsed.hostname:
            self.host = parsed.hostname
        else:
            raise ValueError("Invalid hostname from: %s", self.url)

        if parsed.port:
            self.port = parsed.port

        if scheme == "ws":
            if not self.port:
                self.port = 80
        elif scheme == "wss":
            if not self.port:
                self.port = 443
        else:
            raise ValueError("Invalid scheme: %s" % scheme)

        if parsed.path:
            resource = parsed.path
        else:
            resource = "/"

        if parsed.query:
            resource += "?" + parsed.query

        self.scheme = scheme
        self.resource = resource

    def close(self, code=1000, reason=''):
        """
        Initiate the closing handshake with the server.
        """
        if not self.client_terminated:
            self.client_terminated = True
            self.sock.sendall(self.stream.close(code=code, reason=reason).single(mask=True))

    def connect(self):
        """
        Connects this websocket and starts the upgrade handshake
        with the remote endpoint.
        """
        if self.scheme == "wss":
            # default port is now 443; upgrade self.sender to send ssl
            self.sock = ssl.wrap_socket(self.sock)

        self.sock.connect((self.host, int(self.port)))

        self.sock.sendall(self.handshake_request)

        response = enc('')
        doubleCLRF = enc('\r\n\r\n')
        while True:
            bytes = self.sock.recv(128)
            if not bytes:
                break
            response += bytes
            if doubleCLRF in response:
                break

        if not response:
            self.close_connection()
            raise HandshakeError("Invalid response")

        headers, _, body = response.partition(doubleCLRF)
        response_line, _, headers = headers.partition(enc('\r\n'))

        try:
            self.process_response_line(response_line)
            self.protocols, self.extensions = self.process_handshake_header(headers)
        except HandshakeError:
            self.close_connection()
            raise

        self.handshake_ok()
        if body:
            self.process(body)

    @property
    def handshake_headers(self):
        """
        List of headers appropriate for the upgrade
        handshake.
        """
        headers = [
            ('Host', self.host),
            ('Connection', 'Upgrade'),
            ('Upgrade', 'websocket'),
            ('Sec-WebSocket-Key', dec(self.key)),
            ('Origin', self.url),
            ('Sec-WebSocket-Version', str(max(WS_VERSION)))
            ]

        if self.protocols:
            headers.append(('Sec-WebSocket-Protocol', ','.join(self.protocols)))

        return headers

    @property
    def handshake_request(self):
        """
        Prepare the request to be sent for the upgrade handshake.
        """
        headers = self.handshake_headers
        request = ["GET %s HTTP/1.1" % self.resource]
        for header, value in headers:
            request.append("%s: %s" % (header, value))
        request.append('\r\n')

        return enc('\r\n'.join(request))

    def process_response_line(self, response_line):
        """
        Ensure that we received a HTTP `101` status code in
        response to our request and if not raises :exc:`HandshakeError`.
        """
        protocol, code, status = response_line.split(enc(' '), 2)
        if code != enc('101'):
            raise HandshakeError("Invalid response status: %s %s" % (code, status))

    def process_handshake_header(self, headers):
        """
        Read the upgrade handshake's response headers and
        validate them against :rfc:`6455`.
        """
        protocols = []
        extensions = []

        headers = headers.strip()

        for header_line in headers.split(enc('\r\n')):
            header, value = header_line.split(enc(':'), 1)
            header = header.strip().lower()
            value = value.strip().lower()

            if header == 'upgrade' and value != 'websocket':
                raise HandshakeError("Invalid Upgrade header: %s" % value)

            elif header == 'connection' and value != 'upgrade':
                raise HandshakeError("Invalid Connection header: %s" % value)

            elif header == 'sec-websocket-accept':
                match = b64encode(sha1(enc(self.key + WS_KEY)).digest())
                if value != match.lower():
                    raise HandshakeError("Invalid challenge response: %s" % value)

            elif header == 'sec-websocket-protocol':
                protocols = ','.join(value)

            elif header == 'sec-websocket-extensions':
                extensions = ','.join(value)

        return protocols, extensions
