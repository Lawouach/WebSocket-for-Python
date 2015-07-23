# -*- coding: utf-8 -*-
import time
import itertools
import unittest

try:
    from itertools import izip_longest as zip_longest
except ImportError:
    from itertools import zip_longest

from mock import MagicMock, call, patch

from ws4py.manager import WebSocketManager, SelectPoller,\
     EPollPoller
from ws4py.websocket import WebSocket

class WSManagerTest(unittest.TestCase):
    @patch('ws4py.manager.SelectPoller')
    def test_add_and_remove_websocket(self, MockSelectPoller):
        m = WebSocketManager(poller=MockSelectPoller())

        ws = MagicMock()
        ws.sock.fileno.return_value = 1
        
        m.add(ws)
        m.poller.register.assert_called_once_with(1)

        m.remove(ws)
        m.poller.unregister.assert_called_once_with(1)
        
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
        m.poller.unregister.assert_called_once_with(1)
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
        time.sleep(0.2)
        
        ws.terminate.assert_called_once_with()
        
        m.stop()
    
    @patch('ws4py.manager.SelectPoller')
    def test_websocket_close_all(self, MockSelectPoller):
        m = WebSocketManager(poller=MockSelectPoller())

        ws = MagicMock()
        m.add(ws)
        m.close_all()
        ws.close.assert_called_once_with(code=1001, reason='Server is shutting down')
        
    @patch('ws4py.manager.SelectPoller')
    def test_broadcast(self, MockSelectPoller):
        m = WebSocketManager(poller=MockSelectPoller())

        ws = MagicMock()
        ws.terminated = False
        m.add(ws)

        m.broadcast(b'hello there')
        ws.send.assert_called_once_with(b'hello there', False)
        
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

class WSSelectPollerTest(unittest.TestCase):
    @patch('ws4py.manager.select')
    def test_release_poller(self, select):
        poller = SelectPoller()
        select.select.return_value = (poller._fds, None, None)
        
        poller.register(0)
        poller.register(1)
        fd = poller.poll()
        self.assertEqual(fd, [0, 1])

        poller.unregister(0)
        fd = poller.poll()
        self.assertEqual(fd, [1])
        
        poller.release()
        fd = poller.poll()
        self.assertEqual(fd, [])
         
    def test_timeout_when_no_registered_fds(self):
        poller = SelectPoller(timeout=0.5)
        a = time.time()
        fd = poller.poll()
        b = time.time()
        self.assertEqual(fd, [])

        d = b - a 
        if not (0.48 < d < 0.52):
            self.fail("Did not wait for the appropriate amount of time: %f" % d)

    @patch('ws4py.manager.select')
    def test_register_twice_does_not_duplicate_fd(self, select):
        poller = SelectPoller()
        select.select.return_value = (poller._fds, None, None)
        poller.register(0)
        poller.register(0)
        fd = poller.poll()
        self.assertEqual(fd, [0])
            
    def test_unregister_twice_has_no_side_effect(self):
        poller = SelectPoller()
        poller.register(0)
        poller.unregister(0)
        try:
            poller.unregister(0)
        except Exception as ex:
            self.fail("Shouldn't have failed: %s" % ex)
            
     
class FakeEpoll(object):
    def __init__(self):
        self.fds = []

    def close(self):
        self.fds = []

    def register(self, fd, mask):
        if fd in self.fds:
            raise IOError("Already registered")

        self.fds.append(fd)

    def unregister(self, fd):
        # epoll's documentation doesn't say anything
        # about removing fds that are not registered
        # yet/any longer
        if fd in self.fds:
            self.fds.remove(fd)

    def poll(self, timeout):
        # this isn't really what's happening
        # inside but we're not testing
        # epoll afterall
        if not self.fds:
            time.sleep(timeout)
            return []

        # fake EPOLLIN
        return zip_longest(self.fds, '', fillvalue=1)
        
class WSEPollPollerTest(unittest.TestCase):
    @patch('ws4py.manager.select')
    def test_release_poller(self, select):
        select.epoll.return_value = FakeEpoll()
        poller = EPollPoller()
        
        poller.register(0)
        poller.register(1)
        fd = poller.poll()
        self.assertEqual(list(fd), [0, 1])

        poller.unregister(0)
        fd = poller.poll()
        self.assertEqual(list(fd), [1])
        
        poller.release()
        fd = poller.poll()
        self.assertEqual(list(fd), [])
         
    @patch('ws4py.manager.select')
    def test_timeout_when_no_registered_fds(self, select):
        select.epoll.return_value = FakeEpoll()
        poller = EPollPoller(timeout=0.5)
        
        a = time.time()
        fd = list(poller.poll())
        b = time.time()
        self.assertEqual(fd, [])

        d = b - a
        if not (0.48 < d < 0.52):
            self.fail("Did not wait for the appropriate amount of time: %f" % d)

    @patch('ws4py.manager.select')
    def test_register_twice_does_not_duplicate_fd(self, select):
        select.epoll.return_value = FakeEpoll()
        poller = EPollPoller()
        poller.register(0)
        poller.register(0)  # IOError is swallowed
        fd = poller.poll()
        self.assertEqual(list(fd), [0])
            
    @patch('ws4py.manager.select')
    def test_unregister_twice_has_no_side_effect(self, select):
        select.epoll.return_value = FakeEpoll()
        poller = EPollPoller()
        poller.register(0)
        poller.unregister(0)
        try:
            poller.unregister(0)
        except Exception as ex:
            self.fail("Shouldn't have failed: %s" % ex)
            
if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [WSManagerTest, WSSelectPollerTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
