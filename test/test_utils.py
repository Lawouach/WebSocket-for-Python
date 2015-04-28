# -*- coding: utf-8 -*-
import unittest

from ws4py import format_addresses
from ws4py.websocket import WebSocket
from mock import MagicMock

class WSUtilities(unittest.TestCase):
    def test_format_address(self):
        m = MagicMock()
        m.getsockname.return_value = ('127.0.0.1', 52300, None, None)
        m.getpeername.return_value = ('127.0.0.1', 4800, None, None)
        ws = WebSocket(sock=m)

        log = format_addresses(ws)
        self.assertEqual(log, "[Local => 127.0.0.1:52300 | Remote => 127.0.0.1:4800]")
        
if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [WSUtilities]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
