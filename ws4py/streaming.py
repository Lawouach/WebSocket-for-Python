# -*- coding: utf-8 -*-
from ws4py.messaging import TextMessage, BinaryMessage, CloseControlMessage,\
     PingControlMessage, PongControlMessage
from ws4py.framing import Frame, OPCODE_CONTINUATION, OPCODE_TEXT, \
     OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG
from ws4py.exc import FrameTooLargeException, ProtocolException,\
     TextFrameEncodingException, UnsupportedFrameTypeException, StreamClosed

class Stream(object):
    def __init__(self):
        self.messages = []
        self.pings = []
        self.closing = None
        self.errors = []
        self.parser = self.receiver()
        self.parser.next()

    def text_message(self, text):
        return TextMessage(text=text)

    def binary_message(self, bytes):
        return BinaryMessage(bytes)

    @property
    def has_messages(self):
        if self.messages:
            if self.messages[-1].completed:
                return True

        return False

    def close(self, code=1000, reason=''):
        return CloseControlMessage(code=code, reason=reason).single()

    def ping(self, data=''):
        return PingControlMessage(data).single()

    def pong(self, data=''):
        return PongControlMessage(data).single()

    def receiver(self):
        running = True
        while running:
            frame = Frame()
            while True:
                try:
                    bytes = (yield frame.parser.next())
                    frame.parser.send(bytes)
                except StopIteration:
                    bytes = frame.body or ''
                    if frame.masking_key:
                        bytes = frame.unmask(bytes)
                        
                    if frame.opcode == OPCODE_TEXT:
                        try:
                            m = TextMessage(bytes.decode("utf-8", "replace"))
                            m.completed = (frame.fin == 1)
                            self.messages.append(m)
                        except:
                            raise TextFrameEncodingException()

                    elif frame.opcode == OPCODE_BINARY:
                        m = BinaryMessage(bytes)
                        m.completed = (frame.fin == 1)
                        self.messages.append(m)

                    elif frame.opcode == OPCODE_CONTINUATION:
                        m = self.messages[-1]
                        m.completed = (frame.fin == 1)
                        if m.opcode == OPCODE_TEXT:
                            m.extend(bytes.decode("utf-8", "replace"))
                        else:
                            m.extend(bytes)
                        
                    elif frame.opcode == OPCODE_CLOSE:
                        self.closing = CloseControlMessage(reason=bytes.decode("utf-8", "replace"))
                        
                    elif frame.opcode == OPCODE_PING:
                        self.pings.append(PingControlMessage(bytes.decode("utf-8", "replace")))

                    elif frame.opcode == OPCODE_PONG:
                        print "Pong received: %s" % bytes
                            
                    else:
                        raise UnsupportedFrameTypeException()

                    break

                except ProtocolException:
                    self.errors.append(CloseControlMessage(code=1002))
                except FrameTooLargeException:
                    self.errors.append(CloseControlMessage(code=1004))
                except TextFrameEncodingException:
                    self.errors.append(CloseControlMessage(code=1007))
                except UnsupportedFrameTypeException:
                    self.errors.append(CloseControlMessage(code=1003))
                except StreamClosed:
                    running = False
                    break
                
            frame.parser.close()
