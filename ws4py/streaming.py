# -*- coding: utf-8 -*-
import struct

from ws4py.utf8validator import Utf8Validator
from ws4py.messaging import TextMessage, BinaryMessage, CloseControlMessage,\
     PingControlMessage, PongControlMessage
from ws4py.framing import Frame, OPCODE_CONTINUATION, OPCODE_TEXT, \
     OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG
from ws4py.exc import FrameTooLargeException, ProtocolException, InvalidBytesError,\
     TextFrameEncodingException, UnsupportedFrameTypeException, StreamClosed

VALID_CLOSING_CODES = [1000, 1001, 1002, 1003, 1007, 1008, 1009, 1010, 1011]

class Stream(object):
    def __init__(self, always_mask=False, expect_masking=True):
        """
        Represents a websocket stream of bytes flowing in and out.

        The stream doesn't know about the data provider itself and
        doesn't even know about sockets. Instead the stream simply
        yields for more bytes whenever it requires it. The stream owner
        is responsible to provide the stream with those bytes until
        a frame can be interpreted.

        >>> s = Stream()
        >>> s.parser.send(BYTES)
        >>> s.has_messages
        False
        >>> s.parser.send(MORE_BYTES)
        >>> s.has_messages
        True
        >>> s.messages.pop()
        <TextMessage ... >

        @param always_mask: if set, every single frame is masked
        """
        self.message = None
        """
        Parsed test or binary messages. Whenever the parser
        reads more bytes from a fragment message, those bytes
        are appended to the most recent message.
        """

        self.pings = []
        """
        Parsed ping control messages. They are instances of
        messaging.PingControlMessage
        """
        
        self.pongs = []
        """
        Parsed pong control messages. They are instances of
        messaging.PongControlMessage
        """
        
        self.closing = None
        """
        Parsed close control messsage. Instance of
        messaging.CloseControlMessage
        """
        
        self.errors = []
        """
        Detected errors while parsing. Instances of
        messaging.CloseControlMessage
        """
        
        self.parser = self.receiver()
        """
        Parser in charge to process bytes it is fed with.
        """

        # Python generators must be initialized once.
        self.parser.next()

        self.always_mask = always_mask
        self.expect_masking = expect_masking

    def release(self):
        self.message = None
        self.parser.close()
        self.parser = None
        self.errors = None
        self.pings = None
        self.pongs = None
        
        
    def text_message(self, text):
        """
        Returns a messaging.TextMessage instance
        ready to be built. Convenience method so
        that the caller doesn't need to import the
        TextMessage class itself.

        @param text: data to be carried by the message
        """
        return TextMessage(text=text)

    def binary_message(self, bytes):
        """
        Returns a messaging.BinaryMessage instance
        ready to be built. Convenience method so
        that the caller doesn't need to import the
        BinaryMessage class itself.

        @param text: data to be carried by the message
        """
        return BinaryMessage(bytes)

    @property
    def has_message(self):
        """
        Checks if the stream has received any message
        which, if fragmented, is completed.
        """
        if self.message is not None:
            return self.message.completed

        return False

    def close(self, code=1000, reason=''):
        """
        Returns a close control message built from
        a messaging.CloseControlMessage instance.

        @param code: closing status code
        @param reason: status message
        @return: bytes representing a close control single framed message
        """
        return CloseControlMessage(code=code, reason=reason)

    def ping(self, data=''):
        """
        Returns a ping control message built from
        a messaging.PingControlMessage instance.

        @param data: ping data
        @return: bytes representing a ping single framed message
        """
        return PingControlMessage(data).single(mask=self.always_mask)

    def pong(self, data=''):
        """
        Returns a ping control message built from
        a messaging.PongControlMessage instance.

        @param data: pong data
        @return: bytes representing a pong single framed message
        """
        return PongControlMessage(data).single(mask=self.always_mask)

    def receiver(self):
        """
        Parser that keeps trying to interpret bytes it is fed with as
        incoming frames part of a message.

        Control message are single frames only while data messages, like text
        and binary, may be fragmented accross frames.

        The way it works is by instanciating a framing.Frame object,
        then running its parser generator which yields how much bytes
        it requires to performs its task. The stream parser yields this value
        to its caller and feeds the frame parser.

        When the frame parser raises StopIteration, the stream parser
        tries to make sense of the parsed frame. It dispatches the frame's bytes
        to the most appropriate message type based on the frame's opcode.

        Overall this makes the stream parser totally agonstic to
        the data provider.
        """
        utf8validator = Utf8Validator()
        running = True
        while running:
            frame = Frame()
            while True:
                try:
                    bytes = (yield frame.parser.next())
                    frame.parser.send(bytes)
                except StopIteration:
                    bytes = frame.body or ''

                    # Let's avoid unmasking when there is no payload
                    if bytes:
                        if frame.masking_key and self.expect_masking:
                            bytes = frame.unmask(bytes)
                        elif not frame.masking_key and self.expect_masking:
                            self.errors.append(CloseControlMessage(code=1002))
                            break
                        elif frame.masking_key and not self.expect_masking:
                            self.errors.append(CloseControlMessage(code=1002))
                            break
                        
                    if frame.opcode == OPCODE_TEXT:
                        if self.message and not self.message.completed:
                            # We got a text frame before we completed the previous one
                            self.errors.append(CloseControlMessage(code=1002))
                            break

                        is_valid = True
                        if bytes:
                            is_valid, _, _, _ = utf8validator.validate(bytes)
                        
                        if is_valid or (not is_valid and frame.fin == 0):
                            m = TextMessage(bytes)
                            m.completed = (frame.fin == 1)
                            self.message = m
                        elif not is_valid and frame.fin == 1:
                            self.errors.append(CloseControlMessage(code=1007))

                    elif frame.opcode == OPCODE_BINARY:
                        m = BinaryMessage(bytes)
                        m.completed = (frame.fin == 1)
                        self.message = m

                    elif frame.opcode == OPCODE_CONTINUATION:
                        m = self.message
                        if m is None:
                            self.errors.append(CloseControlMessage(code=1002))
                            break
                        
                        m.completed = (frame.fin == 1)
                        if m.opcode == OPCODE_TEXT:
                            is_valid = True
                            if bytes:
                                is_valid, _, _, _ = utf8validator.validate(bytes)
                                
                            if is_valid:
                                m.extend(bytes)
                            else:
                                self.errors.append(CloseControlMessage(code=1007))
                        else:
                            m.extend(bytes)

                    elif frame.opcode == OPCODE_CLOSE:
                        code = 1000
                        reason = ""
                        if frame.payload_length == 0:
                            self.closing = CloseControlMessage(code=1000)
                        elif frame.payload_length == 1:
                            self.closing = CloseControlMessage(code=1002)
                        else:
                            try:
                                code = int(struct.unpack("!H", str(bytes[0:2]))[0])
                            except TypeError:
                                code = 1002
                                reason = 'Invalid Closing Frame Code Type'
                            except struct.error, sr:
                                code = 1002
                                reason = 'Failed at decoding closing code'
                            else:
                                # Those codes are reserved or plainly forbidden
                                if code not in VALID_CLOSING_CODES and not (2999 < code < 5000):
                                    reason = 'Invalid Closing Frame Code: %d' % code
                                    code = 1002
                                elif frame.payload_length > 1:
                                    try:
                                        msg = bytes[2:] if frame.masking_key else frame.body[2:]
                                        reason = msg.decode("utf-8")
                                    except UnicodeDecodeError:
                                        code = 1007
                                        reason = ''
                            self.closing = CloseControlMessage(code=code, reason=reason)
                        
                    elif frame.opcode == OPCODE_PING:
                        self.pings.append(PingControlMessage(bytes))

                    elif frame.opcode == OPCODE_PONG:
                        self.pongs.append(PongControlMessage(bytes))
                    
                    else:
                        self.errors.append(CloseControlMessage(code=1003))

                    break
                    
                except ProtocolException:
                    self.errors.append(CloseControlMessage(code=1002))
                except FrameTooLargeException:
                    self.errors.append(CloseControlMessage(code=1002))
                except StreamClosed:
                    running = False
                    break

            frame.body = None
            frame.parser.close()
            utf8validator.reset()
            
        utf8validator = None
