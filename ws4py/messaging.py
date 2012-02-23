# -*- coding: utf-8 -*-
import os
import struct
import copy

from ws4py.framing import Frame, OPCODE_CONTINUATION, OPCODE_TEXT, \
     OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG

__all__ = ['Message', 'TextMessage', 'BinaryMessage', 'CloseControlMessage',
           'PingControlMessage', 'PongControlMessage']

class Message(object):
    def __init__(self, opcode, data='', encoding='utf-8'):
        """
        A message is a application level entity. It's usually built
        from one or many frames. The protocol defines several kind
        of messages which are grouped into two sets:

        * data messages which can be text or binary typed
        * control messages which provide a mechanism to perform
          in-band control communication between peers

        The ``opcode`` indicates the message type and ``data`` is
        the possible message payload.

        The payload is held internally as a a :func:`bytearray` as they are
        faster than pure strings for append operations.

        Unicode data will be encoded using the provided ``encoding``.
        """
        self.opcode = opcode
        self._completed = False

        if isinstance(data, basestring):
            if isinstance(data, unicode):
                data = data.encode(encoding)
            # bytarrays are way faster than strings
            self.data = bytearray(data)
        elif isinstance(data, bytearray):
            self.data = data
        else:
            raise TypeError("'%s' is not a supported message data type" % type(data))
            
        self.encoding = encoding
        
    def single(self, mask=False):
        """
        Returns a frame bytes with the fin bit set and a random mask.

        If ``mask`` is set, automatically mask the frame
        using a generated 4-byte token.
        """
        mask = os.urandom(4) if mask else None
        return Frame(body=self.data or '', opcode=self.opcode,
                     masking_key=mask, fin=1).build()

    def fragment(self, first=False, last=False, mask=False):
        """
        Returns a :class:`ws4py.framing.Frame` bytes.

        The behavior depends on the given flags:

        * ``first``: the frame uses ``self.opcode`` else a continuation opcode
        * ``last``: the frame has its ``fin`` bit set
        * ``mask``: the frame is masked using a automatically generated 4-byte token
        """
        fin = 1 if last is True else 0
        opcode = self.opcode if first is True else OPCODE_CONTINUATION
        mask = os.urandom(4) if mask else None
        return Frame(body=self.data or '',
                     opcode=opcode, masking_key=mask,
                     fin=fin).build()

    @property
    def completed(self):
        """
        Indicates the the message is complete, meaning
        the frame's ``fin`` bit was set.
        """
        return self._completed

    @completed.setter
    def completed(self, state):
        """
        Sets the state for this message. Usually
        set by the stream's parser.
        """
        self._completed = state
        
    def extend(self, data):
        """
        Add more ``data`` to the message.
        """
        if isinstance(data, unicode):
            data = data.encode(self.encoding)
        self.data.extend(data)
        
    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)

    def __unicode__(self):
        return unicode(self.data, self.encoding or 'utf-8')

class TextMessage(Message):
    def __init__(self, text=None):
        Message.__init__(self, OPCODE_TEXT, text)

    @property
    def is_binary(self):
        return False

    @property
    def is_text(self):
        return True

class BinaryMessage(Message):
    def __init__(self, bytes=None):
        Message.__init__(self, OPCODE_BINARY, bytes, encoding=None)

    @property
    def is_binary(self):
        return True

    @property
    def is_text(self):
        return False

class CloseControlMessage(Message):
    def __init__(self, code=1000, reason=''):
        data = ""
        if code:
            data += struct.pack("!H", code)
        if reason:
            data += reason.encode('utf-8')
            
        Message.__init__(self, OPCODE_CLOSE, data)
        self.code = code
        self.reason = reason

    def __str__(self):
        return self.reason

    def __unicode__(self):
        return self.reason.decode('utf-8')

class PingControlMessage(Message):
    def __init__(self, data=None):
        Message.__init__(self, OPCODE_PING, data)
        
class PongControlMessage(Message):
    def __init__(self, data):
        Message.__init__(self, OPCODE_PONG, data)
