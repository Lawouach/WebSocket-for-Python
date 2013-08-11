# -*- coding: utf-8 -*-
import os
import unittest

from ws4py.framing import Frame, \
     OPCODE_CONTINUATION, OPCODE_TEXT, \
     OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG
from ws4py.messaging import *
from ws4py.compat import *

class WSMessagingTest(unittest.TestCase):
    def test_bytearray_text_message(self):
        m = TextMessage(bytearray(u'\xe9trange', 'utf-8'))
        self.assertFalse(m.is_binary)
        self.assertTrue(m.is_text)
        self.assertEqual(m.opcode, OPCODE_TEXT)
        self.assertEqual(m.encoding, 'utf-8')
        self.assertIsInstance(m.data, bytes)
        # length is compted on the unicode representation
        self.assertEqual(len(m), 7)
        # but once encoded it's actually taking 8 bytes in UTF-8
        self.assertEqual(len(m.data), 8)
        self.assertEqual(m.data, u'\xe9trange'.encode('utf-8'))

        f = m.single()
        self.assertIsInstance(f, bytes)
        self.assertEqual(len(f), 10)  # no masking

        f = m.single(mask=True)
        self.assertIsInstance(f, bytes)
        self.assertEqual(len(f), 14)  # mask takes 4 bytes

        self.assertEqual(m.fragment(first=True, last=True), m.single())

        m.extend(bytearray(' oui', 'utf-8'))
        self.assertEqual(m.data, u'\xe9trange oui'.encode('utf-8'))

    def test_bytes_text_message(self):
        m = TextMessage(u'\xe9trange'.encode('utf-8'))
        self.assertEqual(m.opcode, OPCODE_TEXT)
        self.assertEqual(m.encoding, 'utf-8')
        self.assertIsInstance(m.data, bytes)
        self.assertFalse(m.is_binary)
        self.assertTrue(m.is_text)
        # length is compted on the unicode representation
        self.assertEqual(len(m), 7)
        # but once encoded it's actually taking 8 bytes in UTF-8
        self.assertEqual(len(m.data), 8)
        self.assertEqual(m.data, u'\xe9trange'.encode('utf-8'))

        f = m.single()
        self.assertIsInstance(f, bytes)
        self.assertEqual(len(f), 10)  # no masking

        f = m.single(mask=True)
        self.assertIsInstance(f, bytes)
        self.assertEqual(len(f), 14)  # mask takes 4 bytes

        self.assertEqual(m.fragment(first=True, last=True), m.single())

        m.extend(b' oui')
        self.assertEqual(m.data, u'\xe9trange oui'.encode('utf-8'))

    def test_unicode_text_message(self):
        m = TextMessage(u'\xe9trange')
        self.assertEqual(m.opcode, OPCODE_TEXT)
        self.assertEqual(m.encoding, 'utf-8')
        self.assertIsInstance(m.data, bytes)
        self.assertFalse(m.is_binary)
        self.assertTrue(m.is_text)
        # length is compted on the unicode representation
        self.assertEqual(len(m), 7)
        # but once encoded it's actually taking 8 bytes in UTF-8
        self.assertEqual(len(m.data), 8)
        self.assertEqual(m.data, u'\xe9trange'.encode('utf-8'))

        f = m.single()
        self.assertIsInstance(f, bytes)
        self.assertEqual(len(f), 10)  # no masking

        f = m.single(mask=True)
        self.assertIsInstance(f, bytes)
        self.assertEqual(len(f), 14)  # mask takes 4 bytes

        self.assertEqual(m.fragment(first=True, last=True), m.single())

        m.extend(u' oui')
        self.assertEqual(m.data, u'\xe9trange oui'.encode('utf-8'))

    def test_unicode_text_message_with_no_encoding(self):
        self.assertRaises(TypeError, Message, OPCODE_TEXT, u'\xe9trange', encoding=None)

    def test_invalid_text_message_data_type(self):
        self.assertRaises(TypeError, TextMessage, ['something else'])
        m = TextMessage(u'\xe9trange')
        self.assertRaises(TypeError, m.extend, ["list aren't supported types"])

    def test_close_control_message(self):
        m = CloseControlMessage(reason=u'bye bye')
        self.assertEqual(m.opcode, OPCODE_CLOSE)
        self.assertEqual(m.encoding, 'utf-8')
        self.assertIsInstance(m.reason, bytes)
        self.assertEqual(len(m), 7)
        self.assertEqual(m.code, 1000)
        self.assertEqual(m.reason, b'bye bye')
        
    def test_ping_control_message(self):
        m = PingControlMessage(data=u'are you there?')
        self.assertEqual(m.opcode, OPCODE_PING)
        self.assertEqual(m.encoding, 'utf-8')
        self.assertIsInstance(m.data, bytes)
        self.assertEqual(len(m), 14)
        
    def test_pong_control_message(self):
        m = PongControlMessage(data=u'yes, I am')
        self.assertEqual(m.opcode, OPCODE_PONG)
        self.assertEqual(m.encoding, 'utf-8')
        self.assertIsInstance(m.data, bytes)
        self.assertEqual(len(m), 9)
        

if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [WSMessagingTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
