# -*- coding: utf-8 -*-
import os
import socket
import time
import unittest

from mock import MagicMock, call

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import EchoWebSocket
from ws4py.framing import Frame, OPCODE_TEXT, OPCODE_CLOSE

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
        self.assertEqual(len(manager), 0)

        s = MagicMock(spec=socket.socket)
        s.recv.return_value = Frame(opcode=OPCODE_TEXT, body=b'hello',
                                    fin=1, masking_key=os.urandom(4)).build()
        h = EchoWebSocket(s, [], [])
        cherrypy.engine.publish('handle-websocket', h, ('127.0.0.1', 0))
        self.assertEqual(len(manager), 1)
        self.assertTrue(h in manager)

        # the following call to .close() on the
        # websocket object will initiate
        # the closing handshake
        # This next line mocks the response
        # from the client to actually
        # complete the handshake.
        # The manager will then remove the websocket
        # from its pool
        s.recv.return_value = Frame(opcode=OPCODE_CLOSE, body=b"ok we're done",
                                    fin=1, masking_key=os.urandom(4)).build()
        h.close()

        # the poller runs a thread, give it time to get there
        # just wait up to 5 seconds.
        left_iteration = 50
        while left_iteration:
            left_iteration -= 1
            time.sleep(.1)
            if len(manager) == 0:
                break

        self.assertEqual(len(manager), 0)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [CherryPyTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
