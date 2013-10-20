# -*- coding: utf-8 -*-
import time
import unittest

from mock import MagicMock, call, patch

from ws4py.manager import WebSocketManager
from ws4py.websocket import WebSocket

class WSManagerTest(unittest.TestCase):
    @patch('ws4py.manager.SelectPoller')
    def test_add_and_remove_websocket(self, MockSelectPoller):
        m = WebSocketManager(poller=MockSelectPoller())

        ws = MagicMock()
        ws.sock.fileno.return_value = 1
        
        m.add(ws)
        m.poller.register.assert_call_once_with(ws)

        m.remove(ws)
        m.poller.unregister.assert_call_once_with(ws)
        
    @patch('ws4py.manager.SelectPoller')
    def test_cannot_add_websocket_more_than_once(self, MockSelectPoller):
        m = WebSocketManager(poller=MockSelectPoller())

        ws = MagicMock()
        ws.sock.fileno.return_value = 1
        
        m.add(ws)
        self.assertEqual(len(m), 1)
        
        m.add(ws)
        self.assertEqual(len(m), 1)
        
    @patch('ws4py.manager.SelectPoller')
    def test_cannot_remove_unregistered_websocket(self, MockSelectPoller):
        m = WebSocketManager(poller=MockSelectPoller())

        ws = MagicMock()
        ws.sock.fileno.return_value = 1
        
        m.remove(ws)
        self.assertEqual(len(m), 0)
        self.assertFalse(m.poller.unregister.called)
        
        m.add(ws)
        self.assertEqual(len(m), 1)
        m.remove(ws)
        self.assertEqual(len(m), 0)
        m.poller.unregister.assert_call_once_with(ws)
        m.poller.reset_mock()
        
        m.remove(ws)
        self.assertEqual(len(m), 0)
        self.assertFalse(m.poller.unregister.called)

    @patch('ws4py.manager.SelectPoller')
    def test_mainloop_can_be_stopped_when_no_websocket_were_registered(self, MockSelectPoller):
        m = WebSocketManager(poller=MockSelectPoller())
        self.assertFalse(m.running)
        
        m.start()
        self.assertTrue(m.running)

        m.stop()
        self.assertFalse(m.running)
        
    @patch('ws4py.manager.SelectPoller')
    def test_mainloop_can_be_stopped(self, MockSelectPoller):
        m = WebSocketManager(poller=MockSelectPoller())
        
        def poll():
            yield 1
            m.stop()
            yield 2
            
        m.poller.poll.return_value = poll()
        self.assertFalse(m.running)
        
        m.start()
        # just make sure it had the time to finish
        time.sleep(0.1)
        self.assertFalse(m.running)
        
    @patch('ws4py.manager.SelectPoller')
    def test_websocket_terminated_from_mainloop(self, MockSelectPoller):
        m = WebSocketManager(poller=MockSelectPoller())
        m.poller.poll.return_value = [1]

        ws = MagicMock()
        
        ws.terminated = False
        ws.sock.fileno.return_value = 1
        ws.once.return_value = False
        
        m.add(ws)
        m.start()
        
        ws.terminate.assert_call_once_with()
        
        m.stop()
    
    @patch('ws4py.manager.SelectPoller')
    def test_websocket_close_all(self, MockSelectPoller):
        m = WebSocketManager(poller=MockSelectPoller())

        ws = MagicMock()
        m.add(ws)
        m.close_all()
        ws.terminate.assert_call_once_with(1001, 'Server is shutting down')
        
    @patch('ws4py.manager.SelectPoller')
    def test_broadcast(self, MockSelectPoller):
        m = WebSocketManager(poller=MockSelectPoller())

        ws = MagicMock()
        ws.terminated = False
        m.add(ws)

        m.broadcast(b'hello there')
        ws.send.assert_call_once_with(b'hello there')
        
    @patch('ws4py.manager.SelectPoller')
    def test_broadcast_failure_must_not_break_caller(self, MockSelectPoller):
        m = WebSocketManager(poller=MockSelectPoller())

        ws = MagicMock()
        ws.terminated = False
        ws.send.side_effect = RuntimeError
        m.add(ws)

        try:
                m.broadcast(b'hello there')
        except:
                self.fail("Broadcasting shouldn't have failed")
                
if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [WSManagerTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
