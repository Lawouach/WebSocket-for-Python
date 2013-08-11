# -*- coding: utf-8 -*-
import unittest
import os
import socket
import struct

from mock import MagicMock, call

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
        m = MagicMock()
        m.recv.return_value = b''
        ws = WebSocket(sock=m)
        self.assertFalse(ws.once())


if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [WSWebSocketTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
