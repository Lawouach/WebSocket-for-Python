# -*- coding: utf-8 -*-
import array
import os
import struct

from ws4py.exc import FrameTooLargeException, ProtocolException

# Frame opcodes defined in the spec.
OPCODE_CONTINUATION = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xa

__all__ = ['Frame']

class Frame(object):
    def __init__(self, opcode=None, body='', masking_key=None, fin=0, rsv1=0, rsv2=0, rsv3=0):
        self.opcode = opcode
        self.body = body
        self.masking_key = masking_key
        self.fin = fin
        self.rsv1 = rsv1
        self.rsv2 = rsv2
        self.rsv3 = rsv3
        self.payload_length = len(body)

        self.parser = self._parser()
        self.parser.next()

    def build(self):
        header = ''

        if self.fin > 0x1:
            raise ValueError('FIN bit parameter must be 0 or 1')

        if 0x3 <= self.opcode <= 0x7 or 0xB <= self.opcode:
            raise ValueError('Opcode cannot be a reserved opcode')
    
        ## +-+-+-+-+-------+
        ## |F|R|R|R| opcode|
        ## |I|S|S|S|  (4)  |
        ## |N|V|V|V|       |
        ## | |1|2|3|       |
        ## +-+-+-+-+-------+
        header += chr(((self.fin << 7)
                       | (self.rsv1 << 6)
                       | (self.rsv2 << 5)
                       | (self.rsv3 << 4)
                       | self.opcode))

        ##                 +-+-------------+-------------------------------+
        ##                 |M| Payload len |    Extended payload length    |
        ##                 |A|     (7)     |             (16/63)           |
        ##                 |S|             |   (if payload len==126/127)   |
        ##                 |K|             |                               |
        ## +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
        ## |     Extended payload length continued, if payload len == 127  |
        ## + - - - - - - - - - - - - - - - +-------------------------------+
        if self.masking_key: mask_bit = 1 << 7
        else: mask_bit = 0

        length = self.payload_length 
        if length < 126:
            header += chr(mask_bit | length)
        elif length < (1 << 16):
            header += chr(mask_bit | 126) + struct.pack('!H', length)
        elif length < (1 << 63):
            header += chr(mask_bit | 127) + struct.pack('!Q', length)
        else:
            raise FrameTooLargeException()

        ## + - - - - - - - - - - - - - - - +-------------------------------+
        ## |                               |Masking-key, if MASK set to 1  |
        ## +-------------------------------+-------------------------------+
        ## | Masking-key (continued)       |          Payload Data         |
        ## +-------------------------------- - - - - - - - - - - - - - - - +
        ## :                     Payload Data continued ...                :
        ## + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
        ## |                     Payload Data continued ...                |
        ## +---------------------------------------------------------------+
        if not self.masking_key:
            return header + self.body 

        bytes = header + self.masking_key + self.mask(self.body)
        return str(bytes)

    def _parser(self):
        buf = ''
        bytes = ''
        
        while not bytes or len(bytes) < 1:
            bytes = (yield 1)

        first_byte = ord(bytes[0])
        self.fin = (first_byte >> 7) & 1
        self.rsv1 = (first_byte >> 6) & 1
        self.rsv2 = (first_byte >> 5) & 1
        self.rsv3 = (first_byte >> 4) & 1
        self.opcode = first_byte & 0xf

        if self.fin not in [0, 1]:
            raise ProtocolException()

        if bytes and len(bytes) > 1:
            buf = bytes[1:]
            bytes = buf
        else:
            bytes = ''

        while not bytes or len(bytes) < 1:
            bytes = (yield 1)
 
        second_byte = ord(bytes[0])
        mask = (second_byte >> 7) & 1
        self.payload_length = second_byte & 0x7f

        if self.opcode == OPCODE_CLOSE:
            raise StopIteration()

        if bytes and len(bytes) > 1:
            buf = bytes[1:]
            bytes = buf
        else:
            buf = ''
            bytes = ''

        # The spec doesn't disallow putting a value in 0x0-0xFFFF into the
        # 8-octet extended payload length field (or 0x0-0xFD in 2-octet field).
        # So, we don't check the range of extended_payload_length.
        if self.payload_length == 127:
            if len(buf) < 8:
                nxt_buf_size = 8 - len(buf)
                bytes = (yield nxt_buf_size)
                bytes = buf + (bytes or '')
                while len(bytes) < 8:
                    b = (yield 8 - len(bytes))
                    if isinstance(b, basestring):
                        bytes = bytes + b
                if len(bytes) > 8:
                    buf = bytes[8:]
            else:
                bytes = buf[:8]
                buf = buf[8:]
            extended_payload_length = bytes
            self.payload_length = struct.unpack(
                '!Q', extended_payload_length)[0]
            if self.payload_length > 0x7FFFFFFFFFFFFFFF:
                raise FrameTooLargeException()
        elif self.payload_length == 126:
            if len(buf) < 2:
                nxt_buf_size = 2 - len(buf)
                bytes = (yield nxt_buf_size)
                bytes = buf + (bytes or '')
                while len(bytes) < 2:
                    b = (yield 2 - len(bytes))
                    if isinstance(b, basestring):
                        bytes = bytes + b
                if len(bytes) > 2:
                    buf = bytes[2:]
            else:
                bytes = buf[:2]
                buf = buf[2:]
            extended_payload_length = bytes
            self.payload_length = struct.unpack(
                '!H', extended_payload_length)[0]
            
        if mask:
            if len(buf) < 4:
                nxt_buf_size = 4 - len(buf)
                bytes = (yield nxt_buf_size)
                bytes = buf + (bytes or '')
                while not bytes or len(bytes) < 4:
                    bytes = bytes + (yield 4 - len(bytes))
                if len(bytes) > 4:
                    buf = bytes[4:]
            else:
                bytes = buf[:4]
                buf = buf[4:]
            self.masking_key = bytes

        if len(buf) < self.payload_length:
            nxt_buf_size = self.payload_length - len(buf)
            bytes = (yield nxt_buf_size)
            bytes = buf + (bytes or '')
            while len(bytes) < self.payload_length:
                l = self.payload_length - len(bytes)
                b = (yield l)
                if isinstance(b, basestring):
                    bytes = bytes + b
        else:
            bytes = buf[:self.payload_length]

        self.body = bytes
        yield
        
    def mask(self, data):
        masked = bytearray(data)
        key = map(ord, self.masking_key)
        for i in range(len(data)):
            masked[i] = masked[i] ^ key[i%4]
        return masked

    unmask = mask
