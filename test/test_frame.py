# -*- coding: utf-8 -*-
import os
import unittest
import types
import random
from struct import pack, unpack

from ws4py.framing import Frame, \
     OPCODE_CONTINUATION, OPCODE_TEXT, \
     OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG
from ws4py.exc import FrameTooLargeException, ProtocolException
from ws4py.compat import *

def map_on_bytes(f, bytes):
    for index, byte in enumerate(bytes):
        f(bytes[index:index+1])

class WSFrameBuilderTest(unittest.TestCase):
    def test_7_bit_length(self):
        f = Frame(opcode=OPCODE_TEXT,
                  body=b'', fin=1)
        self.assertEqual(len(f.build()), 2)

        f = Frame(opcode=OPCODE_TEXT,
                  body=b'*' * 125, fin=1)
        self.assertEqual(len(f.build()), 127)

        mask = os.urandom(4)
        f = Frame(opcode=OPCODE_TEXT,
                  body=b'', masking_key=mask, fin=1)
        self.assertEqual(len(f.build()), 6)

        f = Frame(opcode=OPCODE_TEXT,
                  body=b'*' * 125, masking_key=mask, fin=1)
        self.assertEqual(len(f.build()), 131)

    def test_16_bit_length(self):
        f = Frame(opcode=OPCODE_TEXT,
                  body=b'*' * 126, fin=1)
        self.assertEqual(len(f.build()), 130)

        f = Frame(opcode=OPCODE_TEXT,
                  body=b'*' * 65535, fin=1)
        self.assertEqual(len(f.build()), 65539)

        mask = os.urandom(4)
        f = Frame(opcode=OPCODE_TEXT,
                  body=b'*' * 126, masking_key=mask, fin=1)
        self.assertEqual(len(f.build()), 134)

        f = Frame(opcode=OPCODE_TEXT,
                  body=b'*' * 65535, masking_key=mask, fin=1)
        self.assertEqual(len(f.build()), 65543)

    def test_63_bit_length(self):
        f = Frame(opcode=OPCODE_TEXT,
                  body=b'*' * 65536, fin=1)
        self.assertEqual(len(f.build()), 65546)

        mask = os.urandom(4)
        f = Frame(opcode=OPCODE_TEXT,
                  body=b'*' * 65536, masking_key=mask, fin=1)
        self.assertEqual(len(f.build()), 65550)

    def test_non_zero_nor_one_fin(self):
        f = Frame(opcode=OPCODE_TEXT,
                  body=b'', fin=2)
        self.assertRaises(ValueError, f.build)

    def test_opcodes(self):
        for opcode in [OPCODE_CONTINUATION, OPCODE_TEXT,
                       OPCODE_BINARY, OPCODE_CLOSE,
                       OPCODE_PING, OPCODE_PONG]:
            f = Frame(opcode=opcode, body=b'', fin=1)
            byte = ord(f.build()[0])
            self.assertTrue(byte & opcode == opcode)

        f = Frame(opcode=0x3, body=b'', fin=1)
        self.assertRaises(ValueError, f.build)

    def test_masking(self):
        if py3k: mask = b"7\xfa!="
        else: mask = "7\xfa!="
        f = Frame(opcode=OPCODE_TEXT,
                  body=b'Hello',
                  masking_key=mask, fin=1)

        if py3k: spec_says = b'\x81\x857\xfa!=\x7f\x9fMQX'
        else: spec_says = '\x81\x857\xfa!=\x7f\x9fMQX'
        self.assertEqual(f.build(), spec_says)

    def test_frame_too_large(self):
        f = Frame(opcode=OPCODE_TEXT, body=b'', fin=1)
        # fake huge length
        f.payload_length = 1 << 63
        self.assertRaises(FrameTooLargeException, f.build)

    def test_passing_encoded_string(self):
        # once encoded the u'\xe9' character will be of length 2
        f = Frame(opcode=OPCODE_TEXT, body=u'\xe9trange'.encode('utf-8'), fin=1)
        self.assertEqual(len(f.build()), 10)

    def test_passing_unencoded_string_raises_type_error(self):
        self.assertRaises(TypeError, Frame, opcode=OPCODE_TEXT, body=u'\xe9', fin=1)

class WSFrameParserTest(unittest.TestCase):
    def test_frame_parser_is_a_generator(self):
        f = Frame()
        self.assertEqual(type(f.parser), types.GeneratorType)
        f.parser.close()
        self.assertRaises(StopIteration, next, f.parser)

    def test_frame_header_parsing(self):
        bytes = Frame(opcode=OPCODE_TEXT, body=b'hello', fin=1).build()

        f = Frame()
        self.assertEqual(f.parser.send(bytes[0:1]), 1)
        self.assertEqual(f.fin, 1)
        self.assertEqual(f.rsv1, 0)
        self.assertEqual(f.rsv2, 0)
        self.assertEqual(f.rsv3, 0)
        self.assertEqual(f.parser.send(bytes[1:2]), 5)
        self.assertTrue(f.masking_key is None)
        self.assertEqual(f.payload_length, 5)
        f.parser.close()

    def test_frame_payload_parsing(self):
        bytes = Frame(opcode=OPCODE_TEXT, body=b'hello', fin=1).build()

        f = Frame()
        self.assertEqual(f.parser.send(bytes[0:1]), 1)
        self.assertEqual(f.parser.send(bytes[1:2]), 5)
        f.parser.send(bytes[2:])
        self.assertEqual(f.body, b'hello')

        f = Frame()
        f.parser.send(bytes)
        self.assertRaises(StopIteration, next, f.parser)
        self.assertEqual(f.body, b'hello')

    def test_incremental_parsing_small_7_bit_length(self):
        bytes = Frame(opcode=OPCODE_TEXT, body=b'hello', fin=1).build()

        f = Frame()
        map_on_bytes(f.parser.send, bytes)
        self.assertTrue(f.masking_key is None)
        self.assertEqual(f.payload_length, 5)

    def test_incremental_parsing_16_bit_length(self):
        bytes = Frame(opcode=OPCODE_TEXT, body=b'*' * 126, fin=1).build()

        f = Frame()
        map_on_bytes(f.parser.send, bytes)
        self.assertTrue(f.masking_key is None)
        self.assertEqual(f.payload_length, 126)

    def test_incremental_parsing_63_bit_length(self):
        bytes = Frame(opcode=OPCODE_TEXT, body=b'*' * 65536, fin=1).build()

        f = Frame()
        map_on_bytes(f.parser.send, bytes)
        self.assertTrue(f.masking_key is None)
        self.assertEqual(f.payload_length, 65536)

    def test_rsv1_bits_set(self):
        f = Frame()
        self.assertRaises(ProtocolException, f.parser.send, b'\x40')

    def test_rsv2_bits_set(self):
        f = Frame()
        self.assertRaises(ProtocolException, f.parser.send, b'\x20')

    def test_rsv3_bits_set(self):
        f = Frame()
        self.assertRaises(ProtocolException, f.parser.send, b'\x10')

    def test_invalid_opcode(self):
        for opcode in range(3, 9):
            f = Frame()
            self.assertRaises(ProtocolException, f.parser.send, chr(opcode))

        f = Frame()
        self.assertRaises(ProtocolException, f.parser.send, chr(10))

    def test_fragmented_control_frame_is_invalid(self):
        f = Frame()
        self.assertRaises(ProtocolException, f.parser.send, b'0x9')

    def test_fragmented_control_frame_is_too_large(self):
        bytes = Frame(opcode=OPCODE_PING, body=b'*'*65536, fin=1).build()
        f = Frame()
        self.assertRaises(FrameTooLargeException, f.parser.send, bytes)

    def test_frame_sized_127(self):
        body = b'*'*65536
        bytes = Frame(opcode=OPCODE_TEXT, body=body, fin=1).build()

        f = Frame()
        # determine how the size is stored
        f.parser.send(bytes[:3])
        self.assertTrue(f.masking_key is None)
        # that's a large frame indeed
        self.assertEqual(f.payload_length, 127)

        # this will compute the actual application data size
        # it will also read the first byte of data
        # indeed the length is found from byte 3 to 10
        f.parser.send(bytes[3:11])
        self.assertEqual(f.payload_length, 65536)
        
        # parse the rest of our data
        f.parser.send(bytes[11:])
        self.assertEqual(f.body, body)

        
        # The same but this time we provide enough
        # bytes so that the application's data length
        # can be computed from the first generator's send call
        f = Frame()
        f.parser.send(bytes[:10])
        self.assertTrue(f.masking_key is None)
        self.assertEqual(f.payload_length, 65536)
        
        # parse the rest of our data
        f.parser.send(bytes[10:])
        self.assertEqual(f.body, body)
        
        
        # The same with masking given out gradually
        mask = os.urandom(4)
        bytes = Frame(opcode=OPCODE_TEXT, body=body, fin=1, masking_key=mask).build()
        f = Frame()
        f.parser.send(bytes[:10])
        self.assertTrue(f.masking_key is None)
        self.assertEqual(f.payload_length, 65536)
        
        # parse the mask gradually
        f.parser.send(bytes[10:12])
        f.parser.send(bytes[12:])
        self.assertEqual(f.unmask(f.body), body)
        
    def test_frame_too_large_with_7_bit_length(self):
        header = pack('!B', ((1 << 7)
                             | (0 << 6)
                             | (0 << 5)
                             | (0 << 4)
                             | OPCODE_TEXT))
        header += pack('!B', 127) + pack('!Q', 1 << 63)
        b = bytes(header + b'')
        f = Frame()
        self.assertRaises(FrameTooLargeException, f.parser.send, b)

    def test_not_sensitive_to_overflow(self):
        header = pack('!B', ((1 << 7)
                             | (0 << 6)
                             | (0 << 5)
                             | (0 << 4)
                             | OPCODE_TEXT))
        header += pack('!B', 126) + pack('!H', 256)
        b = bytes(header + b'*' * 512)
        f = Frame()
        f.parser.send(b)
        # even though we tried to inject 512 bytes, we
        # still only read 256
        self.assertEqual(len(f.body), 256)
        
    def test_frame_sized_126(self):
        body = b'*'*256
        bytes = Frame(opcode=OPCODE_TEXT, body=body, fin=1).build()

        f = Frame()
        # determine how the size is stored
        f.parser.send(bytes[:3])
        self.assertTrue(f.masking_key is None)
        # that's a large frame indeed
        self.assertEqual(f.payload_length, 126)

        # this will compute the actual application data size
        # it will also read the first byte of data
        # indeed the length is found from byte 3 to 10
        f.parser.send(bytes[3:11])
        self.assertEqual(f.payload_length, 256)
        
        # parse the rest of our data
        f.parser.send(bytes[11:])
        self.assertEqual(f.body, body)
        
        
        # The same but this time we provide enough
        # bytes so that the application's data length
        # can be computed from the first generator's send call
        f = Frame()
        f.parser.send(bytes[:10])
        self.assertTrue(f.masking_key is None)
        self.assertEqual(f.payload_length, 256)
        
        # parse the rest of our data
        f.parser.send(bytes[10:])
        self.assertEqual(f.body, body)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in (WSFrameBuilderTest, WSFrameParserTest,):
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
