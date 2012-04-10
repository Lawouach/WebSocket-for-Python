# -*- coding: utf-8 -*-
import unittest
import os
import struct

from ws4py.framing import Frame, \
     OPCODE_CONTINUATION, OPCODE_TEXT, \
     OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG
from ws4py.streaming import Stream
from ws4py.messaging import CloseControlMessage

class WSStreamTest(unittest.TestCase):
    def test_empty_close_message(self):
        f = Frame(opcode=OPCODE_CLOSE, body='', fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(s.closing, None)
        s.parser.send(f)
        self.assertEqual(type(s.closing), CloseControlMessage)
    
    def test_too_large_close_message(self):
        payload = struct.pack("!H", 1000) + '*' * 330
        f = Frame(opcode=OPCODE_CLOSE, body=payload, fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(len(s.errors), 0)
        self.assertEqual(s.closing, None)
        s.parser.send(f)
        self.assertEqual(s.closing, None)
        
        self.assertEqual(len(s.errors), 1)
        self.assertEqual(type(s.errors[0]), CloseControlMessage)
        self.assertEqual(s.errors[0].code, 1002)
    
    def test_ping_message_received(self):
        msg = 'ping me'
        f = Frame(opcode=OPCODE_PING, body=msg, fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(len(s.pings), 0)
        s.parser.send(f)
        self.assertEqual(len(s.pings), 1)
    
        
    def test_text_message_received(self):
        msg = 'hello there'
        f = Frame(opcode=OPCODE_TEXT, body=msg, fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(len(s.messages), 0)
        s.parser.send(f)
        self.assertEqual(len(s.messages), 1)
    
    def test_incremental_text_message_received(self):
        msg = 'hello there'
        f = Frame(opcode=OPCODE_TEXT, body=msg, fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(s.has_message, False)
        for byte in f:
            s.parser.send(byte)
        self.assertEqual(s.has_message, True)
    
    def test_text_message_received(self):
        msg = 'hello there'
        f = Frame(opcode=OPCODE_TEXT, body=msg, fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(s.has_message, False)
        s.parser.send(f)
        self.assertEqual(s.message.completed, True)

    def test_text_message_with_continuation_received(self):
        msg = 'hello there'
        f = Frame(opcode=OPCODE_TEXT, body=msg, fin=0, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(s.has_message, False)
        s.parser.send(f)
        self.assertEqual(s.message.completed, False)

        for i in range(3):
            f = Frame(opcode=OPCODE_CONTINUATION, body=msg, fin=0, masking_key=os.urandom(4)).build()
            s.parser.send(f)
            self.assertEqual(s.has_message, False)
            self.assertEqual(s.message.completed, False)
            self.assertEqual(s.message.opcode, OPCODE_TEXT)
        
        f = Frame(opcode=OPCODE_CONTINUATION, body=msg, fin=1, masking_key=os.urandom(4)).build()
        s.parser.send(f)
        self.assertEqual(s.has_message, True)
        self.assertEqual(s.message.completed, True)
        self.assertEqual(s.message.opcode, OPCODE_TEXT)
        
    def test_text_message_with_continuation_and_ping_in_between(self):
        msg = 'hello there'
        key = os.urandom(4)
        f = Frame(opcode=OPCODE_TEXT, body=msg, fin=0, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(s.has_message, False)
        s.parser.send(f)
        self.assertEqual(s.message.completed, False)

        for i in range(3):
            f = Frame(opcode=OPCODE_CONTINUATION, body=msg, fin=0, masking_key=os.urandom(4)).build()
            s.parser.send(f)
            self.assertEqual(s.has_message, False)
            self.assertEqual(s.message.completed, False)
            self.assertEqual(s.message.opcode, OPCODE_TEXT)
        
            f = Frame(opcode=OPCODE_PING, body='ping me', fin=1, masking_key=os.urandom(4)).build()
            self.assertEqual(len(s.pings), i)
            s.parser.send(f)
            self.assertEqual(len(s.pings), i+1)
        
        f = Frame(opcode=OPCODE_CONTINUATION, body=msg, fin=1, masking_key=os.urandom(4)).build()
        s.parser.send(f)
        self.assertEqual(s.has_message, True)
        self.assertEqual(s.message.opcode, OPCODE_TEXT)
        self.assertEqual(s.message.completed, True)
        
    def test_binary_message_received(self):
        msg = os.urandom(16)
        f = Frame(opcode=OPCODE_BINARY, body=msg, fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(s.has_message, False)
        s.parser.send(f)
        self.assertEqual(s.message.completed, True)

    def test_binary_message_with_continuation_received(self):
        msg = os.urandom(16)
        key = os.urandom(4)
        f = Frame(opcode=OPCODE_BINARY, body=msg, fin=0, masking_key=key).build()
        s = Stream()
        self.assertEqual(s.has_message, False)
        s.parser.send(f)
        self.assertEqual(s.has_message, False)

        for i in range(3):
            f = Frame(opcode=OPCODE_CONTINUATION, body=msg, fin=0, masking_key=key).build()
            s.parser.send(f)
            self.assertEqual(s.has_message, False)
            self.assertEqual(s.message.completed, False)
            self.assertEqual(s.message.opcode, OPCODE_BINARY)
        
        f = Frame(opcode=OPCODE_CONTINUATION, body=msg, fin=1, masking_key=key).build()
        s.parser.send(f)
        self.assertEqual(s.has_message, True)
        self.assertEqual(s.message.completed, True)
        self.assertEqual(s.message.opcode, OPCODE_BINARY)
        
if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [WSStreamTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
