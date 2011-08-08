# -*- coding: utf-8 -*-
import os

from ws4py.framing import Frame, OPCODE_CONTINUATION, OPCODE_TEXT, \
     OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG

__all__ = ['TextMessage', 'BinaryMessage', 'CloseControlMessage',
           'PingControlMessage', 'PongControlMessage']

class Message(object):
    def __init__(self, opcode, data=''):
        self.opcode = opcode
        self.data = data
        self._completed = False
        
    def single(self):
        return Frame(body=self.data, opcode=self.opcode,
                     masking_key=os.urandom(4), fin=1).build()

    def fragment(self, first=False, last=False):
        fin = 1 if last is True else 0
        opcode = self.opcode if first is True else OPCODE_CONTINUATION
        return Frame(body=self.data, opcode=opcode,
                     masking_key=os.urandom(4), fin=fin).build()

    @property
    def completed(self):
        return self._completed

    @completed.setter
    def completed(self, state):
        self._completed = state
        
    def extend(self, data):
        self.data = self.data + data

class TextMessage(Message):
    def __init__(self, text=None):
        Message.__init__(self, OPCODE_TEXT, text)

    def __str__(self):
        return self.data

class BinaryMessage(Message):
    def __init__(self, bytes=None):
        Message.__init__(self, OPCODE_BINARY, bytes)

class CloseControlMessage(Message):
    def __init__(self, code=1000, reason=''):
        Message.__init__(self, OPCODE_CLOSE, reason)
        self.code = code
        self.reason = reason

class PingControlMessage(Message):
    def __init__(self, data=None):
        Message.__init__(self, OPCODE_PING, data)
        
class PongControlMessage(Message):
    def __init__(self, data):
        Message.__init__(self, OPCODE_PONG, data)
