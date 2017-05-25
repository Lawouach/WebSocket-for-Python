# -*- coding: utf-8 -*-
from base64 import b64encode
from hashlib import sha1
import socket
import time
import unittest

from mock import MagicMock, patch

from ws4py import WS_KEY
from ws4py.exc import HandshakeError
from ws4py.framing import Frame, OPCODE_TEXT, OPCODE_CLOSE
from ws4py.client import WebSocketBaseClient
from ws4py.client.threadedclient import WebSocketClient

class BasicClientTest(unittest.TestCase):
    def test_invalid_hostname_in_url(self):
        self.assertRaises(ValueError, WebSocketBaseClient, url="qsdfqsd65qsd354")

    def test_invalid_scheme_in_url(self):
        self.assertRaises(ValueError, WebSocketBaseClient, url="ftp://localhost")

    def test_invalid_hostname_in_url(self):
        self.assertRaises(ValueError, WebSocketBaseClient, url="ftp://?/")

    def test_parse_unix_schemes(self):
        c = WebSocketBaseClient(url="ws+unix:///my.socket")
        self.assertEqual(c.scheme, "ws+unix")
        self.assertEqual(c.host, "localhost")
        self.assertIsNone(c.port)
        self.assertEqual(c.unix_socket_path, "/my.socket")
        self.assertEqual(c.resource, "/")
        self.assertEqual(c.bind_addr, "/my.socket")

        c = WebSocketBaseClient(url="wss+unix:///my.socket")
        self.assertEqual(c.scheme, "wss+unix")
        self.assertEqual(c.host, "localhost")
        self.assertIsNone(c.port)
        self.assertEqual(c.unix_socket_path, "/my.socket")
        self.assertEqual(c.resource, "/")
        self.assertEqual(c.bind_addr, "/my.socket")

    def test_parse_ws_scheme(self):
        c = WebSocketBaseClient(url="ws://127.0.0.1/")
        self.assertEqual(c.scheme, "ws")
        self.assertEqual(c.host, "127.0.0.1")
        self.assertEqual(c.port, 80)
        self.assertEqual(c.resource, "/")
        self.assertEqual(c.bind_addr, ("127.0.0.1", 80))

    def test_parse_ws_scheme_when_missing_resource(self):
        c = WebSocketBaseClient(url="ws://127.0.0.1")
        self.assertEqual(c.scheme, "ws")
        self.assertEqual(c.host, "127.0.0.1")
        self.assertEqual(c.port, 80)
        self.assertEqual(c.resource, "/")
        self.assertEqual(c.bind_addr, ("127.0.0.1", 80))

    def test_parse_ws_scheme_with_port(self):
        c = WebSocketBaseClient(url="ws://127.0.0.1:9090")
        self.assertEqual(c.scheme, "ws")
        self.assertEqual(c.host, "127.0.0.1")
        self.assertEqual(c.port, 9090)
        self.assertEqual(c.resource, "/")
        self.assertEqual(c.bind_addr, ("127.0.0.1", 9090))

    def test_parse_ws_scheme_with_query_string(self):
        c = WebSocketBaseClient(url="ws://127.0.0.1/?token=value")
        self.assertEqual(c.scheme, "ws")
        self.assertEqual(c.host, "127.0.0.1")
        self.assertEqual(c.port, 80)
        self.assertEqual(c.resource, "/?token=value")
        self.assertEqual(c.bind_addr, ("127.0.0.1", 80))

    def test_parse_wss_scheme(self):
        c = WebSocketBaseClient(url="wss://127.0.0.1/")
        self.assertEqual(c.scheme, "wss")
        self.assertEqual(c.host, "127.0.0.1")
        self.assertEqual(c.port, 443)
        self.assertEqual(c.resource, "/")
        self.assertEqual(c.bind_addr, ("127.0.0.1", 443))

    def test_parse_wss_scheme_when_missing_resource(self):
        c = WebSocketBaseClient(url="wss://127.0.0.1")
        self.assertEqual(c.scheme, "wss")
        self.assertEqual(c.host, "127.0.0.1")
        self.assertEqual(c.port, 443)
        self.assertEqual(c.resource, "/")
        self.assertEqual(c.bind_addr, ("127.0.0.1", 443))

    def test_parse_wss_scheme_with_port(self):
        c = WebSocketBaseClient(url="wss://127.0.0.1:9090")
        self.assertEqual(c.scheme, "wss")
        self.assertEqual(c.host, "127.0.0.1")
        self.assertEqual(c.port, 9090)
        self.assertEqual(c.resource, "/")
        self.assertEqual(c.bind_addr, ("127.0.0.1", 9090))

    def test_parse_wss_scheme_with_query_string(self):
        c = WebSocketBaseClient(url="wss://127.0.0.1/?token=value")
        self.assertEqual(c.scheme, "wss")
        self.assertEqual(c.host, "127.0.0.1")
        self.assertEqual(c.port, 443)
        self.assertEqual(c.resource, "/?token=value")
        self.assertEqual(c.bind_addr, ("127.0.0.1", 443))

    @patch('ws4py.client.socket')
    def test_connect_and_close(self, sock):

        s = MagicMock()
        sock.socket.return_value = s
        sock.getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 0, "",
                                          ("127.0.0.1", 80, 0, 0))]

        c = WebSocketBaseClient(url="ws://127.0.0.1/?token=value")

        s.recv.return_value = b"\r\n".join([
            b"HTTP/1.1 101 Switching Protocols",
            b"Connection: Upgrade",
            b"Sec-Websocket-Version: 13",
            b"Content-Type: text/plain;charset=utf-8",
            b"Sec-Websocket-Accept: " + b64encode(sha1(c.key + WS_KEY).digest()),
            b"Sec-WebSocket-Protocol: proto1, proto2",
            b"Sec-WebSocket-Extensions: ext1, ext2",
            b"Sec-WebSocket-Extensions: ext3",
            b"Upgrade: websocket",
            b"Date: Sun, 26 Jul 2015 12:32:55 GMT",
            b"Server: ws4py/test",
            b"\r\n"
        ])

        c.connect()
        s.connect.assert_called_once_with(("127.0.0.1", 80))
        self.assertEqual(c.protocols, [b'proto1', b'proto2'])
        self.assertEqual(c.extensions, [b'ext1', b'ext2', b'ext3'])

        s.reset_mock()
        c.close(code=1006, reason="boom")
        args = s.sendall.call_args_list[0]
        f = Frame()
        f.parser.send(args[0][0])
        f.parser.close()
        self.assertIn(b'boom', f.unmask(f.body))

    @patch('ws4py.client.socket')
    def test_empty_response(self, sock):

        s = MagicMock()
        sock.socket.return_value = s
        sock.getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 0, "",
                                          ("127.0.0.1", 80, 0, 0))]

        c = WebSocketBaseClient(url="ws://127.0.0.1/?token=value")

        s.recv.return_value = b""
        self.assertRaises(HandshakeError, c.connect)
        s.shutdown.assert_called_once_with(socket.SHUT_RDWR)
        s.close.assert_called_once_with()

    @patch('ws4py.client.socket')
    def test_invalid_response_code(self, sock):

        s = MagicMock()
        sock.socket.return_value = s
        sock.getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 0, "",
                                          ("127.0.0.1", 80, 0, 0))]

        c = WebSocketBaseClient(url="ws://127.0.0.1/?token=value")

        s.recv.return_value = b"\r\n".join([
            b"HTTP/1.1 200 Switching Protocols",
            b"Connection: Upgrade",
            b"Sec-Websocket-Version: 13",
            b"Content-Type: text/plain;charset=utf-8",
            b"Sec-Websocket-Accept: " + b64encode(sha1(c.key + WS_KEY).digest()),
            b"Upgrade: websocket",
            b"Date: Sun, 26 Jul 2015 12:32:55 GMT",
            b"Server: ws4py/test",
            b"\r\n"
        ])

        self.assertRaises(HandshakeError, c.connect)
        s.shutdown.assert_called_once_with(socket.SHUT_RDWR)
        s.close.assert_called_once_with()

    @patch('ws4py.client.socket')
    def test_invalid_response_headers(self, sock):

        for key_header, invalid_value in ((b'upgrade', b'boom'),
                                          (b'connection', b'bim')):
            s = MagicMock()
            sock.socket.return_value = s
            sock.getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 0, "",
                                              ("127.0.0.1", 80, 0, 0))]
            c = WebSocketBaseClient(url="ws://127.0.0.1/?token=value")

            status_line = b"HTTP/1.1 101 Switching Protocols"
            headers = {
                b"connection": b"Upgrade",
                b"Sec-Websocket-Version": b"13",
                b"Content-Type": b"text/plain;charset=utf-8",
                b"Sec-Websocket-Accept": b64encode(sha1(c.key + WS_KEY).digest()),
                b"upgrade": b"websocket",
                b"Date": b"Sun, 26 Jul 2015 12:32:55 GMT",
                b"Server": b"ws4py/test"
            }

            headers[key_header] = invalid_value

            request = [status_line] + [k + b" : " + v for (k, v) in headers.items()] + [b'\r\n']
            s.recv.return_value = b"\r\n".join(request)

            self.assertRaises(HandshakeError, c.connect)
            s.shutdown.assert_called_once_with(socket.SHUT_RDWR)
            s.close.assert_called_once_with()
            sock.reset_mock()

class ThreadedClientTest(unittest.TestCase):

    @patch('ws4py.client.socket')
    def setUp(self, sock):
        self.sock = MagicMock(spec=socket.socket)
        sock.socket.return_value = self.sock
        sock.getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 0, "",
                                          ("127.0.0.1", 80, 0, 0))]

        self.client = WebSocketClient(url="ws://127.0.0.1/")

    def _exchange1(self, *args, **kwargs):
        yield b"\r\n".join([
            b"HTTP/1.1 101 Switching Protocols",
            b"Connection: Upgrade",
            b"Sec-Websocket-Version: 13",
            b"Content-Type: text/plain;charset=utf-8",
            b"Sec-Websocket-Accept: " + b64encode(sha1(self.client.key + WS_KEY).digest()),
            b"Upgrade: websocket",
            b"Date: Sun, 26 Jul 2015 12:32:55 GMT",
            b"Server: ws4py/test",
            b"\r\n"
        ])

        for i in range(100):
            time.sleep(0.1)
            yield Frame(opcode=OPCODE_TEXT, body=b'hello',
                        fin=1).build()

    def _exchange2(self, *args, **kwargs):
        yield Frame(opcode=OPCODE_CLOSE, body=b'',
                    fin=1).build()

    def test_thread_is_started_once_connected(self):
        self.sock.recv.side_effect = self._exchange1()
        self.assertFalse(self.client._th.is_alive())

        self.client.connect()
        time.sleep(0.5)
        self.assertTrue(self.client._th.is_alive())

        self.sock.recv.side_effect = self._exchange2()
        time.sleep(0.5)
        self.assertFalse(self.client._th.is_alive())

    def test_thread_is_started_once_connected_secure(self):
        """ Same as the above test, but with SSL socket """
        # pretend the socket is an SSL socket
        self.sock.pending = lambda: False
        self.client._is_secure = True

        self.sock.recv.side_effect = self._exchange1()
        self.assertFalse(self.client._th.is_alive())

        self.client.connect()
        time.sleep(0.5)
        self.assertTrue(self.client._th.is_alive())

        self.sock.recv.side_effect = self._exchange2()
        time.sleep(0.5)
        self.assertFalse(self.client._th.is_alive())


if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [BasicClientTest,
                     ThreadedClientTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
