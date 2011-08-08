# -*- coding: utf-8 -*-
import os
import unittest
import types
import random

from ws4py.framing import Frame, \
     OPCODE_CONTINUATION, OPCODE_TEXT, \
     OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG

class WSFrameBuilderTest(unittest.TestCase):
    def test_7_bit_length(self):
        f = Frame(opcode=OPCODE_TEXT,
                  body='', fin=1)
        self.assertEqual(len(f.build()), 2)
        
        f = Frame(opcode=OPCODE_TEXT,
                  body='*' * 125, fin=1)
        self.assertEqual(len(f.build()), 127)

        mask = os.urandom(4)
        f = Frame(opcode=OPCODE_TEXT,
                  body='', masking_key=mask, fin=1)
        self.assertEqual(len(f.build()), 6)

        f = Frame(opcode=OPCODE_TEXT,
                  body='*' * 125, masking_key=mask, fin=1)
        self.assertEqual(len(f.build()), 131)

    def test_16_bit_length(self):
        f = Frame(opcode=OPCODE_TEXT,
                  body='*' * 126, fin=1)
        self.assertEqual(len(f.build()), 130)

        f = Frame(opcode=OPCODE_TEXT,
                  body='*' * 65535, fin=1)
        self.assertEqual(len(f.build()), 65539)
        
        mask = os.urandom(4)
        f = Frame(opcode=OPCODE_TEXT,
                  body='*' * 126, masking_key=mask, fin=1)
        self.assertEqual(len(f.build()), 134)

        f = Frame(opcode=OPCODE_TEXT,
                  body='*' * 65535, masking_key=mask, fin=1)
        self.assertEqual(len(f.build()), 65543)
        
    def test_63_bit_length(self):
        f = Frame(opcode=OPCODE_TEXT,
                  body='*' * 65536, fin=1)
        self.assertEqual(len(f.build()), 65546)

        mask = os.urandom(4)
        f = Frame(opcode=OPCODE_TEXT,
                  body='*' * 65536, masking_key=mask, fin=1)
        self.assertEqual(len(f.build()), 65550)

    def test_non_zero_nor_one_fin(self):
        f = Frame(opcode=OPCODE_TEXT,
                  body='', fin=2)
        self.assertRaises(ValueError, f.build)

    def test_opcodes(self):
        for opcode in [OPCODE_CONTINUATION, OPCODE_TEXT,
                       OPCODE_BINARY, OPCODE_CLOSE,
                       OPCODE_PING, OPCODE_PONG]:
            f = Frame(opcode=opcode, body='', fin=1)
            byte = ord(f.build()[0])
            self.assertTrue(byte & opcode == opcode)

        f = Frame(opcode=0x3, body='', fin=1)
        self.assertRaises(ValueError, f.build)

    def test_masking(self):
        mask = "7\xfa!="
        f = Frame(opcode=OPCODE_TEXT,
                  body='Hello', masking_key=mask, fin=1)

        spec_says = '\x81\x857\xfa!=\x7f\x9fMQX'
        self.assertEqual(f.build(), spec_says)

class WSFrameParserTest(unittest.TestCase):
    def test_frame_parser_is_a_generator(self):
        f = Frame()
        self.assertEqual(type(f.parser), types.GeneratorType)
        f.parser.close()
        self.assertRaises(StopIteration, f.parser.next)

    def test_frame_header_parsing(self):
        bytes = Frame(opcode=OPCODE_TEXT, body='hello', fin=1).build()

        f = Frame()
        self.assertEqual(f.parser.send(bytes[0]), 1)
        self.assertEqual(f.fin, 1)
        self.assertEqual(f.rsv1, 0)
        self.assertEqual(f.rsv2, 0)
        self.assertEqual(f.rsv3, 0)
        self.assertEqual(f.parser.send(bytes[1]), 5)
        self.assertTrue(f.masking_key is None)
        self.assertEqual(f.payload_length, 5)
        f.parser.close()
        
    def test_frame_payload_parsing(self):
        bytes = Frame(opcode=OPCODE_TEXT, body='hello', fin=1).build()

        f = Frame()
        self.assertEqual(f.parser.send(bytes[0]), 1)
        self.assertEqual(f.parser.send(bytes[1]), 5)
        f.parser.send(bytes[2:])
        self.assertEqual(f.body, 'hello')
        
        f = Frame()
        f.parser.send(bytes)
        self.assertRaises(StopIteration, f.parser.next)
        self.assertEqual(f.body, 'hello')
        
    def test_incremental_parsing_small_7_bit_length(self):
        bytes = Frame(opcode=OPCODE_TEXT, body='hello', fin=1).build()
        
        f = Frame()
        for byte in bytes:
            f.parser.send(byte)
        self.assertTrue(f.masking_key is None)
        self.assertEqual(f.payload_length, 5)

    def test_incremental_parsing_16_bit_length(self):
        bytes = Frame(opcode=OPCODE_TEXT, body='*' * 126, fin=1).build()
        
        f = Frame()
        for byte in bytes:
            f.parser.send(byte)
        self.assertTrue(f.masking_key is None)
        self.assertEqual(f.payload_length, 126)

    def test_incremental_parsing_63_bit_length(self):
        bytes = Frame(opcode=OPCODE_TEXT, body='*' * 65536, fin=1).build()
        
        f = Frame()
        for byte in bytes:
            f.parser.send(byte)
        self.assertTrue(f.masking_key is None)
        self.assertEqual(f.payload_length, 65536)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in (WSFrameBuilderTest, WSFrameParserTest,):
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
