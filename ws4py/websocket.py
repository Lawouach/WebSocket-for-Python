# -*- coding: utf-8 -*-
import base64
import copy
import errno
import logging
import socket
from sys import exc_info
import traceback
import types

from ws4py import WS_KEY, WS_VERSION
from ws4py.exc import HandshakeError, StreamClosed
from ws4py.streaming import Stream
from ws4py.messaging import Message

DEFAULT_READING_SIZE = 2

__all__ = ['WebSocket', 'EchoWebSocket']

class WebSocket(object):
    """ Represents a websocket endpoint and provides a high level interface to drive the endpoint. """
    
    def __init__(self, sock, protocols=None, extensions=None, environ=None):
        """ The ``sock`` is an opened connection
        resulting from the websocket handshake.
        
        If ``protocols`` is provided, it is a list of protocols
        negotiated during the handshake as is ``extensions``.
        
        If ``environ`` is provided, it is a copy of the WSGI environ
        dictionnary from the underlying WSGI server.
        """
        
        self.stream = Stream(always_mask=False)
        """
        Underlying websocket stream that performs the websocket
        parsing to high level objects. By default this stream
        never masks its messages. Clients using this class should
        set the ``stream.always_mask`` fields to ``True``
        and ``stream.expect_masking`` fields to ``False``.
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
        The ``code`` is the status code representing the
        termination's reason.

        Once this method is called, the ``server_terminated``
        attribute is set. Calling this method several times is
        safe as the closing frame will be sent only the first
        time.
        
        .. seealso:: Defined Status Codes http://tools.ietf.org/html/rfc6455#section-7.4.1
        """
        if not self.server_terminated:
            self.server_terminated = True
            self.sender(self.stream.close(code=code, reason=reason).single(mask=self.stream.always_mask))
            
    def closed(self, code, reason=None):
        """
        Called  when the websocket stream and connection are finally closed.
        The provided ``code`` is status set by the other point and
        ``reason`` is a human readable message.

        .. seealso:: Defined Status Codes http://tools.ietf.org/html/rfc6455#section-7.4.1
        """
        pass

    @property
    def terminated(self):
        """
        Returns ``True`` if both the client and server have been
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
        Pong message, as a :class:`messaging.PongControlMessage` instance,
        received on the stream.
        """
        pass

    def received_message(self, message):
        """
        Called whenever a complete ``message``, binary or text,
        is received and ready for application's processing.

        The passed message is an instance of :class:`messaging.TextMessage`
        or :class:`messaging.BinaryMessage`.

        .. note:: You should override this method in your subclass.
        """
        pass

    def send(self, payload, binary=False):
        """
        Sends the given ``payload`` out.

        If ``payload`` is some bytes or a bytearray,
        then it is sent as a single message not fragmented.

        If ``payload`` is a generator, each chunk is sent as part of
        fragmented message.

        If ``binary`` is set, handles the payload as a binary message.
        """
        message_sender = self.stream.binary_message if binary else self.stream.text_message
        
        if isinstance(payload, basestring) or isinstance(payload, bytearray):
            self.sender(message_sender(payload).single(mask=self.stream.always_mask))

        elif isinstance(payload, Message):
            self.sender(payload.single(mask=self.stream.always_mask))
                
        elif type(payload) == types.GeneratorType:
            bytes = payload.next()
            first = True
            for chunk in payload:
                self.sender(message_sender(bytes).fragment(first=first, mask=self.stream.always_mask))
                bytes = chunk
                first = False

            self.sender(message_sender(bytes).fragment(last=True, mask=self.stream.always_mask))
            
        else:
            raise ValueError("Unsupported type '%s' passed to send()" % type(payload))

    def _cleanup(self):
        """
        Frees up resources used by the endpoint.
        """
        self.sender = None
        self.sock = None
        self.environ = None
        self.stream._cleanup()
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
        s = self.stream
        try:
            self.opened()
            sock = self.sock
            fileno = sock.fileno()
            process = self.process
            
            while not self.terminated:
                bytes = sock.recv(self.reading_buffer_size)
                if not process(bytes):
                    break
        finally:
            self.client_terminated = self.server_terminated = True
            
            try:
                if not s.closing:
                    self.closed(1006, "Going away")
                else:
                    self.closed(s.closing.code, s.closing.reason)
            finally:
                s = sock = fileno = process = None
                self.close_connection()
                self._cleanup()


    def process(self, bytes):
        """ Takes some bytes and process them through the
        internal stream's parser. If a message of any kind is
        found, performs one of these actions:

        * A closing message will initiate the closing handshake
        * Errors will initiate a closing handshake
        * A message will be passed to the ``received_message`` method
        * Pings will see pongs be sent automatically
        * Pongs will be passed to the ``ponged`` method

        The process should be terminated when this method
        returns ``False``.
        """
        s = self.stream
        
        if not bytes and self.reading_buffer_size > 0:
            return False

        self.reading_buffer_size = s.parser.send(bytes) or DEFAULT_READING_SIZE

        if s.closing is not None:
            if not self.server_terminated:
                self.close(s.closing.code, s.closing.reason)
            else:
                self.client_terminated = True
            s = None
            return False

        if s.errors:
            for error in s.errors:
                self.close(error.code, error.reason)
            s.errors = []
            s = None
            return False

        if s.has_message:
            self.received_message(s.message)
            s.message.data = None
            s.message = None
            s = None
            return True

        if s.pings:
            for ping in s.pings:
                self.sender(s.pong(ping.data))
            s.pings = []

        if s.pongs:
            for pong in s.pongs:
                self.ponged(pong)
            s.pongs = []

        s = None
        return True
        
class EchoWebSocket(WebSocket):
    def received_message(self, message):
        """
        Automatically sends back the provided ``message`` to
        its originating endpoint.
        """
        self.send(message.data, message.is_binary)
