# -*- coding: utf-8 -*-
import time
import unittest

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import EchoWebSocket

class FakeSocket(object):
    def settimeout(self, timeout):
        pass

    def shutdown(self, flag):
        pass

    def close(self):
        pass

    def sendall(self, bytes):
        return len(bytes)

    def setblocking(self, flag):
        pass

    def fileno(self):
        return 1

    def recv(self, bufsize=0):
        pass

    def getsockname(self):
        return '127.0.0.1', 0

    def getpeername(self):
        return '127.0.0.1', 8091

class FakePoller(object):
    def __init__(self, timeout=0.1):
        self._fds = []

    def release(self):
        self._fds = []

    def register(self, fd):
        if fd not in self._fds:
            self._fds.append(fd)

    def unregister(self, fd):
        if fd in self._fds:
            self._fds.remove(fd)

    def poll(self):
        return self._fds

class App(object):
    @cherrypy.expose
    def ws(self):
        assert cherrypy.request.ws_handler != None

def setup_engine():
    # we don't need a HTTP server for this test
    cherrypy.server.unsubscribe()

    cherrypy.config.update({'log.screen': False})

    cherrypy.engine.websocket = WebSocketPlugin(cherrypy.engine)
    cherrypy.engine.websocket.subscribe()

    cherrypy.engine.websocket.manager.poller = FakePoller()

    cherrypy.tools.websocket = WebSocketTool()

    config={'/ws': {'tools.websocket.on': True,
                    'tools.websocket.handler_cls': EchoWebSocket}}
    cherrypy.tree.mount(App(), '/', config)
    cherrypy.engine.start()

def teardown_engine():
    cherrypy.engine.exit()

class CherryPyTest(unittest.TestCase):
    def setUp(self):
        setup_engine()

    def tearDown(self):
        teardown_engine()

    def test_plugin(self):
        manager = cherrypy.engine.websocket.manager
        self.assertEquals(len(manager), 0)

        s = FakeSocket()
        h = EchoWebSocket(s, [], [])
        cherrypy.engine.publish('handle-websocket', h, ('127.0.0.1', 0))
        self.assertEquals(len(manager), 1)
        self.assertIn(h, manager)

        h.close()
        
        # the poller runs a thread, give it time to get there
        time.sleep(0.5)

        # TODO: Implement a fake poller so that works...
        self.assertEquals(len(manager), 0)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [CherryPyTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
