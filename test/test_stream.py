# -*- coding: utf-8 -*-
import unittest
import os
import struct

from ws4py.framing import Frame, \
     OPCODE_CONTINUATION, OPCODE_TEXT, \
     OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG
from ws4py.streaming import Stream
from ws4py.messaging import TextMessage, BinaryMessage, \
     CloseControlMessage, PingControlMessage, PongControlMessage
from ws4py.compat import *

class WSStreamTest(unittest.TestCase):
    def test_empty_close_message(self):
        f = Frame(opcode=OPCODE_CLOSE, body=b'', fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(s.closing, None)
        s.parser.send(f)
        self.assertEqual(type(s.closing), CloseControlMessage)
        self.assertEqual(s.closing.code, 1005)

    def test_missing_masking_key_when_expected(self):
        f = Frame(opcode=OPCODE_TEXT, body=b'hello', fin=1, masking_key=None).build()
        s = Stream(expect_masking=True)
        s.parser.send(f)
        next(s.parser)
        self.assertNotEqual(s.errors, [])
        self.assertIsInstance(s.errors[0], CloseControlMessage)
        self.assertEqual(s.errors[0].code, 1002)

    def test_using_masking_key_when_unexpected(self):
        f = Frame(opcode=OPCODE_TEXT, body=b'hello', fin=1, masking_key=os.urandom(4)).build()
        s = Stream(expect_masking=False)
        s.parser.send(f)
        next(s.parser)
        self.assertNotEqual(s.errors, [])
        self.assertIsInstance(s.errors[0], CloseControlMessage)
        self.assertEqual(s.errors[0].code, 1002)

    def test_text_messages_cannot_interleave(self):
        s = Stream()

        f = Frame(opcode=OPCODE_TEXT, body=b'hello',
                  fin=0, masking_key=os.urandom(4)).build()
        s.parser.send(f)
        next(s.parser)

        f = Frame(opcode=OPCODE_TEXT, body=b'there',
                  fin=1, masking_key=os.urandom(4)).build()
        s.parser.send(f)
        next(s.parser)

        self.assertNotEqual(s.errors, [])
        self.assertIsInstance(s.errors[0], CloseControlMessage)
        self.assertEqual(s.errors[0].code, 1002)

    def test_binary_messages_cannot_interleave(self):
        s = Stream()

        f = Frame(opcode=OPCODE_BINARY, body=os.urandom(2),
                  fin=0, masking_key=os.urandom(4)).build()
        s.parser.send(f)
        next(s.parser)

        f = Frame(opcode=OPCODE_BINARY, body=os.urandom(7),
                  fin=1, masking_key=os.urandom(4)).build()
        s.parser.send(f)
        next(s.parser)

        self.assertNotEqual(s.errors, [])
        self.assertIsInstance(s.errors[0], CloseControlMessage)
        self.assertEqual(s.errors[0].code, 1002)

    def test_binary_and_text_messages_cannot_interleave(self):
        s = Stream()

        f = Frame(opcode=OPCODE_TEXT, body=b'hello',
                  fin=0, masking_key=os.urandom(4)).build()
        s.parser.send(f)
        next(s.parser)

        f = Frame(opcode=OPCODE_BINARY, body=os.urandom(7),
                  fin=1, masking_key=os.urandom(4)).build()
        s.parser.send(f)
        next(s.parser)

        self.assertNotEqual(s.errors, [])
        self.assertIsInstance(s.errors[0], CloseControlMessage)
        self.assertEqual(s.errors[0].code, 1002)

    def test_continuation_frame_before_message_started_is_invalid(self):
        f = Frame(opcode=OPCODE_CONTINUATION, body=b'hello',
                  fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        s.parser.send(f)
        next(s.parser)
        self.assertNotEqual(s.errors, [])
        self.assertIsInstance(s.errors[0], CloseControlMessage)
        self.assertEqual(s.errors[0].code, 1002)

    def test_invalid_encoded_bytes(self):
        f = Frame(opcode=OPCODE_TEXT, body=b'h\xc3llo',
                  fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        s.parser.send(f)
        next(s.parser)
        self.assertNotEqual(s.errors, [])
        self.assertIsInstance(s.errors[0], CloseControlMessage)
        self.assertEqual(s.errors[0].code, 1007)

    def test_invalid_encoded_bytes_on_continuation(self):
        s = Stream()

        f = Frame(opcode=OPCODE_TEXT, body=b'hello',
                  fin=0, masking_key=os.urandom(4)).build()
        s.parser.send(f)
        next(s.parser)

        f = Frame(opcode=OPCODE_CONTINUATION, body=b'h\xc3llo',
                  fin=1, masking_key=os.urandom(4)).build()
        s.parser.send(f)
        next(s.parser)

        self.assertNotEqual(s.errors, [])
        self.assertIsInstance(s.errors[0], CloseControlMessage)
        self.assertEqual(s.errors[0].code, 1007)

    def test_too_large_close_message(self):
        payload = struct.pack("!H", 1000) + b'*' * 330
        f = Frame(opcode=OPCODE_CLOSE, body=payload,
                  fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(len(s.errors), 0)
        self.assertEqual(s.closing, None)
        s.parser.send(f)
        self.assertEqual(s.closing, None)

        self.assertEqual(len(s.errors), 1)
        self.assertEqual(type(s.errors[0]), CloseControlMessage)
        self.assertEqual(s.errors[0].code, 1002)

    def test_invalid_sized_close_message(self):
        payload = b'boom'
        f = Frame(opcode=OPCODE_CLOSE, body=payload,
                  fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(len(s.errors), 0)
        self.assertEqual(s.closing, None)
        s.parser.send(f)
        self.assertEqual(type(s.closing), CloseControlMessage)
        self.assertEqual(s.closing.code, 1005)

    def test_close_message_of_size_one_are_invalid(self):
        payload = b'*'
        f = Frame(opcode=OPCODE_CLOSE, body=payload,
                  fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(len(s.errors), 0)
        self.assertEqual(s.closing, None)
        s.parser.send(f)
        self.assertEqual(type(s.closing), CloseControlMessage)
        self.assertEqual(s.closing.code, 1005)

    def test_invalid_close_message_type(self):
        payload = struct.pack("!H", 1500) + b'hello'
        f = Frame(opcode=OPCODE_CLOSE, body=payload,
                  fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(len(s.errors), 0)
        self.assertEqual(s.closing, None)
        s.parser.send(f)
        self.assertEqual(type(s.closing), CloseControlMessage)
        self.assertEqual(s.closing.code, 1005)

    def test_invalid_close_message_reason_encoding(self):
        payload = struct.pack("!H", 1000) + b'h\xc3llo'
        f = Frame(opcode=OPCODE_CLOSE, body=payload,
                  fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(len(s.errors), 0)
        self.assertEqual(s.closing, None)
        s.parser.send(f)
        self.assertEqual(s.closing, None)
        self.assertEqual(type(s.errors[0]), CloseControlMessage)
        self.assertEqual(s.errors[0].code, 1007)

    def test_protocol_exception_from_frame_parsing(self):
        payload = struct.pack("!H", 1000) + b'hello'
        f = Frame(opcode=OPCODE_CLOSE, body=payload,
                  fin=1, masking_key=os.urandom(4))
        f.rsv1 = 1
        f = f.build()
        s = Stream()
        self.assertEqual(len(s.errors), 0)
        self.assertEqual(s.closing, None)
        s.parser.send(f)
        self.assertEqual(s.closing, None)
        self.assertEqual(type(s.errors[0]), CloseControlMessage)
        self.assertEqual(s.errors[0].code, 1002)

    def test_close_message_received(self):
        payload = struct.pack("!H", 1000) + b'hello'
        f = Frame(opcode=OPCODE_CLOSE, body=payload,
                  fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(s.closing, None)
        s.parser.send(f)
        self.assertEqual(type(s.closing), CloseControlMessage)
        self.assertEqual(s.closing.code, 1000)
        self.assertEqual(s.closing.reason, b'hello')

    def test_ping_message_received(self):
        msg = b'ping me'
        f = Frame(opcode=OPCODE_PING, body=msg, fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(len(s.pings), 0)
        s.parser.send(f)
        self.assertEqual(len(s.pings), 1)

    def test_pong_message_received(self):
        msg = b'pong!'
        f = Frame(opcode=OPCODE_PONG, body=msg, fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(len(s.pongs), 0)
        s.parser.send(f)
        self.assertEqual(len(s.pongs), 1)

    def test_text_message_received(self):
        msg = b'hello there'
        f = Frame(opcode=OPCODE_TEXT, body=msg, fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(len(s.messages), 0)
        s.parser.send(f)
        self.assertEqual(len(s.messages), 1)

    def test_incremental_text_message_received(self):
        msg = b'hello there'
        f = Frame(opcode=OPCODE_TEXT, body=msg, fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(s.has_message, False)
        bytes = f
        for index, byte in enumerate(bytes):
            s.parser.send(bytes[index:index+1])
        self.assertEqual(s.has_message, True)

    def test_text_message_received(self):
        msg = b'hello there'
        f = Frame(opcode=OPCODE_TEXT, body=msg, fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        self.assertEqual(s.has_message, False)
        s.parser.send(f)
        self.assertEqual(s.message.completed, True)

    def test_text_message_with_continuation_received(self):
        msg = b'hello there'
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
        msg = b'hello there'
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

            f = Frame(opcode=OPCODE_PING, body=b'ping me', fin=1, masking_key=os.urandom(4)).build()
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

    def test_helper_with_unicode_text_message(self):
        s = Stream()
        m = s.text_message(u'hello there!')
        self.assertIsInstance(m, TextMessage)
        self.assertFalse(m.is_binary)
        self.assertTrue(m.is_text)
        self.assertEqual(m.opcode, OPCODE_TEXT)
        self.assertEqual(m.encoding, 'utf-8')
        self.assertIsInstance(m.data, bytes)
        self.assertEqual(len(m), 12)
        self.assertEqual(len(m.data), 12)
        self.assertEqual(m.data, b'hello there!')

    def test_helper_with_bytes_text_message(self):
        s = Stream()
        m = s.text_message('hello there!')
        self.assertIsInstance(m, TextMessage)
        self.assertFalse(m.is_binary)
        self.assertTrue(m.is_text)
        self.assertEqual(m.opcode, OPCODE_TEXT)
        self.assertEqual(m.encoding, 'utf-8')
        self.assertIsInstance(m.data, bytes)
        self.assertEqual(len(m), 12)
        self.assertEqual(len(m.data), 12)
        self.assertEqual(m.data, b'hello there!')

    def test_helper_with_binary_message(self):
        msg = os.urandom(16)
        s = Stream()
        m = s.binary_message(msg)
        self.assertIsInstance(m, BinaryMessage)
        self.assertTrue(m.is_binary)
        self.assertFalse(m.is_text)
        self.assertEqual(m.opcode, OPCODE_BINARY)
        self.assertIsInstance(m.data, bytes)
        self.assertEqual(len(m), 16)
        self.assertEqual(len(m.data), 16)
        self.assertEqual(m.data, msg)

    def test_helper_ping_message(self):
        s = Stream()
        m = s.ping('sos')
        self.assertIsInstance(m, bytes)
        self.assertEqual(len(m), 5)

    def test_helper_masked_ping_message(self):
        s = Stream(always_mask=True)
        m = s.ping('sos')
        self.assertIsInstance(m, bytes)
        self.assertEqual(len(m), 9)

    def test_helper_pong_message(self):
        s = Stream()
        m = s.pong('sos')
        self.assertIsInstance(m, bytes)
        self.assertEqual(len(m), 5)

    def test_helper_masked_pong_message(self):
        s = Stream(always_mask=True)
        m = s.pong('sos')
        self.assertIsInstance(m, bytes)
        self.assertEqual(len(m), 9)

    def test_closing_parser_should_release_resources(self):
        f = Frame(opcode=OPCODE_TEXT, body=b'hello',
                  fin=1, masking_key=os.urandom(4)).build()
        s = Stream()
        s.parser.send(f)
        s.parser.close()


if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [WSStreamTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
