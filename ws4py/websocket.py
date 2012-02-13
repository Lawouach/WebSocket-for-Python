# -*- coding: utf-8 -*-
import base64
import copy
import errno
import logging
import socket
from sys import exc_info
import traceback
import types

from ws4py import WS_KEY
from ws4py.exc import HandshakeError, StreamClosed
from ws4py.streaming import Stream
from ws4py.messaging import Message

WS_VERSION = 13
DEFAULT_READING_SIZE = 2

__all__ = ['WebSocket', 'EchoWebSocket']

class WebSocket(object):
    def __init__(self, sock, protocols, extensions, environ=None):
        """
        Represents a websocket endpoint and provides a high level
        interface to drive the endpoint.

        @param sock: opened connection after the websocket upgrade
        @param protocols: list of protocols from the handshake
        @param extensions: list of extensions from the handshake
        @param environ: WSGI environ dictionary coming from the
          underlying WSGI HTTP server, providing the context for
          this connection.
        """
        
        self.stream = Stream(always_mask=False)
        """
        Underlying websocket stream that performs the websocket
        parsing to high level objects. By default this stream
        never masks its messages. Clients using this class should
        set the `stream.always_mask` field to `True`.
        """
        
        self.protocols = protocols
        """
        List of protocols supported by this endpoint.
        Unused for now.
        """
        
        self.extensions = extensions
        """
        List of extensions supported by this endpoint.
        Unused for now.
        """

        self.sock = sock
        """
        Underlying connection.
        """
        
        self.client_terminated = False
        """
        Indicates if the client has been marked as terminated.
        """
        
        self.server_terminated = False
        """
        Indicates if the server has been marked as terminated.
        """

        self.reading_buffer_size = DEFAULT_READING_SIZE
        """
        Current connection reading buffer size.
        """

        self.sender = self.sock.sendall
        
        self.environ = environ
        """
        WSGI environ dictionary.
        """
        
    def opened(self):
        """
        Called by the server when the upgrade handshake
        has succeeeded. 
        """
        pass

    def close(self, code=1000, reason=''):
        """
        Call this method to initiate the websocket connection
        closing by sending a close frame to the connected peer.

        Once this method is called, the `server_terminated`
        attribute is set. Calling this method several times is
        safe as the closing frame will be sent only the first
        time.

        @param code: status code describing why the connection is closed
        @param reason: a human readable message describing why the connection is closed
        """
        if not self.server_terminated:
            self.server_terminated = True
            self.sender(self.stream.close(code=code, reason=reason).single())
            
    def closed(self, code, reason=None):
        """
        Called by the server when the websocket connection
        is finally closed.

        @param code: status code
        @param reason: human readable message of the closing exchange
        """
        pass

    @property
    def terminated(self):
        """
        Returns True if both the client and server have been
        marked as terminated.
        """
        return self.client_terminated is True and self.server_terminated is True
    
    def close_connection(self):
        """
        Shutdowns then closes the underlying connection.
        """
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass

    def ponged(self, pong):
        """
        Pong message received on the stream.

        @param pong: messaging.PongControlMessage instance
        """
        pass

    def received_message(self, message):
        """
        Called whenever a complete message, binary or text,
        is received and ready for application's processing.

        You should override this methid in your subclass.

        @param message: messaging.TextMessage or
          messaging.BinaryMessage instance
        """
        pass

    def send(self, payload, binary=False):
        """
        Sends the given payload out.

        If payload is some bytes or a bytearray,
        then it is sent as a single message not fragmented.

        If payload is a generator, each chunk is sent as part of
        fragmented message.

        @param payload: string, bytes, bytearray or a generator
        @param binary: if set, handles the payload as a binary message
        """
        message_sender = self.stream.binary_message if binary else self.stream.text_message
        
        if isinstance(payload, basestring) or isinstance(payload, bytearray):
            self.sender(message_sender(payload).single())

        elif isinstance(payload, Message):
            self.sender(payload.single())
                
        elif type(payload) == types.GeneratorType:
            bytes = payload.next()
            first = True
            for chunk in payload:
                self.sender(message_sender(bytes).fragment(first=first))
                bytes = chunk
                first = False

            self.sender(message_sender(bytes).fragment(last=True))

    def _cleanup(self):
        """
        Frees up some resources used by the endpoint.
        """
        self.sender = None
        self.stream.release()
        self.stream = None

    def run(self):
        """
        Performs the operation of reading from the underlying
        connection in order to feed the stream of bytes.

        We start with a small size of two bytes to be read
        from the connection so that we can quickly parse an
        incoming frame header. Then the stream indicates
        whatever size must be read from the connection since
        it knows the frame payload length.

        Note that we perform some automatic opererations:

        * On a closing message, we respond with a closing
          message and finally close the connection
        * We respond to pings with pong messages.
        * Whenever an error is raised by the stream parsing,
          we initiate the closing of the connection with the
          appropiate error code.

        This method is blocking and should likely be run
        in a thread.
        """
        self.sock.setblocking(True)
        self.opened()
        try:
            s = self.stream
            sock = self.sock
            fileno = sock.fileno()
            while not self.terminated:
                bytes = sock.recv(self.reading_buffer_size)
                if not bytes and self.reading_buffer_size > 0:
                    break

                self.reading_buffer_size = s.parser.send(bytes) or DEFAULT_READING_SIZE

                if s.closing is not None:
                    if not self.server_terminated:
                        self.close(s.closing.code, s.closing.reason)
                    else:
                        self.client_terminated = True
                    break

                if s.errors:
                    for error in s.errors:
                        self.close(error.code, error.reason)
                    s.errors = []
                    break

                if s.has_message:
                    self.received_message(s.message)
                    s.message.data = None
                    s.message = None
                    continue
                
                if s.pings:
                    for ping in s.pings:
                        self.sender(s.pong(ping.data))
                    s.pings = []

                if s.pongs:
                    for pong in s.pongs:
                        self.ponged(pong)
                    s.pongs = []
        finally:
            self.client_terminated = self.server_terminated = True

            try:
                if not self.stream.closing:
                    self.closed(1006)
            finally:
                self.close_connection()
                self._cleanup()
        
class EchoWebSocket(WebSocket):
    def received_message(self, message):
        self.send(message.data, message.is_binary)
        
