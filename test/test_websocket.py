# -*- coding: utf-8 -*-
import unittest
import os
import socket
import struct

from mock import MagicMock, call, patch

from ws4py.framing import Frame, \
     OPCODE_CONTINUATION, OPCODE_TEXT, \
     OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage, BinaryMessage, \
     CloseControlMessage, PingControlMessage, PongControlMessage
from ws4py.compat import *

class WSWebSocketTest(unittest.TestCase):
    def test_get_ipv4_addresses(self):
        m = MagicMock()
        m.getsockname.return_value = ('127.0.0.1', 52300)
        m.getpeername.return_value = ('127.0.0.1', 4800)
        ws = WebSocket(sock=m)
        self.assertEqual(ws.local_address, ('127.0.0.1', 52300))
        self.assertEqual(ws.peer_address, ('127.0.0.1', 4800))

    def test_get_ipv6_addresses(self):
        m = MagicMock()
        m.getsockname.return_value = ('127.0.0.1', 52300, None, None)
        m.getpeername.return_value = ('127.0.0.1', 4800, None, None)
        ws = WebSocket(sock=m)
        self.assertEqual(ws.local_address, ('127.0.0.1', 52300))
        self.assertEqual(ws.peer_address, ('127.0.0.1', 4800))

    def test_get_underlying_connection(self):
        m = MagicMock()
        ws = WebSocket(sock=m)
        self.assertEqual(ws.connection, m)

    def test_close_connection(self):
        m = MagicMock()
        ws = WebSocket(sock=m)
        ws.close_connection()
        m.shutdown.assert_called_once_with(socket.SHUT_RDWR)
        m.close.assert_called_once_with()
        self.assertIsNone(ws.connection)

        m = MagicMock()
        m.close = MagicMock(side_effect=RuntimeError)
        ws = WebSocket(sock=m)
        ws.close_connection()
        self.assertIsNone(ws.connection)

    def test_terminate_with_closing(self):
        m = MagicMock()
        s = MagicMock()
        c = MagicMock()
        cc = MagicMock()
        
        ws = WebSocket(sock=m)
        with patch.multiple(ws, closed=c, close_connection=cc):
            ws.stream = s
            ws.stream.closing = CloseControlMessage(code=1000, reason='test closing')
            ws.terminate()
            self.assertTrue(ws.client_terminated)
            self.assertTrue(ws.server_terminated)
            self.assertTrue(ws.terminated)
            c.assert_called_once_with(1000, b'test closing')
            cc.assert_called_once_with()
            self.assertIsNone(ws.stream)
            self.assertIsNone(ws.environ)
        
    def test_terminate_without_closing(self):
        m = MagicMock()
        s = MagicMock()
        c = MagicMock()
        cc = MagicMock()
        
        ws = WebSocket(sock=m)
        with patch.multiple(ws, closed=c, close_connection=cc):
            ws.stream = s
            ws.stream.closing = None
            ws.terminate()
            self.assertTrue(ws.client_terminated)
            self.assertTrue(ws.server_terminated)
            self.assertTrue(ws.terminated)
            c.assert_called_once_with(1006, "Going away")
            cc.assert_called_once_with()
            self.assertIsNone(ws.stream)
            self.assertIsNone(ws.environ)
        
    def test_cannot_process_more_data_when_stream_is_terminated(self):
        m = MagicMock()
        ws = WebSocket(sock=m)
        ws.client_terminated = True
        ws.server_terminated = True

        self.assertFalse(ws.once())

    def test_socket_error_on_receiving_more_bytes(self):
        m = MagicMock()
        m.recv = MagicMock(side_effect=socket.error)
        ws = WebSocket(sock=m)
        self.assertFalse(ws.once())
        
    def test_no_bytes_were_read(self):
        m = MagicMock(spec=socket.socket)
        m.recv.return_value = b''
        ws = WebSocket(sock=m)
        self.assertFalse(ws.once())

    def test_send_bytes_without_masking(self):
        tm = TextMessage(b'hello world').single()
        
        m = MagicMock()
        ws = WebSocket(sock=m)
        ws.send(b'hello world')
        m.sendall.assert_called_once_with(tm)
        
    def test_send_bytes_with_masking(self):
        tm = TextMessage(b'hello world').single(mask=True)
        
        m = MagicMock()
        ws = WebSocket(sock=m)
        ws.stream = MagicMock()
        ws.stream.always_mask = True
        ws.stream.text_message.return_value.single.return_value = tm
        
        ws.send(b'hello world')
        m.sendall.assert_called_once_with(tm)
        
    def test_send_message_without_masking(self):
        tm = TextMessage(b'hello world')
        
        m = MagicMock()
        ws = WebSocket(sock=m)
        ws.send(tm)
        m.sendall.assert_called_once_with(tm.single())
        
    def test_send_generator_without_masking(self):
        tm0 = b'hello'
        tm1 = b'world'
        
        def datasource():
            yield tm0
            yield tm1

        gen = datasource()
        
        m = MagicMock()
        ws = WebSocket(sock=m)
        ws.send(gen)
        self.assertEqual(m.sendall.call_count, 2)
        self.assertRaises(StopIteration, next, gen)
        
    def test_sending_unknown_datetype(self):
        m = MagicMock()
        ws = WebSocket(sock=m)
        self.assertRaises(ValueError, ws.send, 123)

    def test_closing_message_received(self):
        s = MagicMock()
        m = MagicMock()
        c = MagicMock()
        
        ws = WebSocket(sock=m)
        with patch.multiple(ws, close=c):
            ws.stream = s
            ws.stream.closing = CloseControlMessage(code=1000, reason='test closing')
            ws.process(b'unused for this test')
            c.assert_called_once_with(1000, b'test closing')
            
    def test_sending_ping(self):
        tm = PingControlMessage("hello").single(mask=False)
        
        m = MagicMock()
        ws = WebSocket(sock=m)
        ws.ping("hello")
        m.sendall.assert_called_once_with(tm)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [WSWebSocketTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
