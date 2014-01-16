# -*- coding: utf-8 -*-
import time
import unittest

from mock import MagicMock, call, patch

from ws4py.manager import WebSocketManager
from ws4py.websocket import WebSocket
from ws4py.client import WebSocketBaseClient
           
class BasicClientTest(unittest.TestCase):
    def test_invalid_hostname_in_url(self):
        self.assertRaises(ValueError, WebSocketBaseClient, url="qsdfqsd65qsd354")
        
    def test_invalid_scheme_in_url(self):
        self.assertRaises(ValueError, WebSocketBaseClient, url="ftp://localhost")
    
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [BasicClientTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
