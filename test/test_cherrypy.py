# -*- coding: utf-8 -*-
import unittest

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.server.handler.threadedhandler import EchoWebSocketHandler

class FakeSocket(object):
    def settimeout(self, timeout):
        pass

    def shutdown(self, flag):
        pass

    def close(self):
        pass

    def sendall(self, bytes):
        return len(bytes)

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
    
    cherrypy.tools.websocket = WebSocketTool()
    
    config={'/ws': {'tools.websocket.on': True,
                    'tools.websocket.handler_cls': EchoWebSocketHandler}}
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
        self.assertEquals(len(cherrypy.engine.websocket.handlers), 0)

        s = FakeSocket()
        h = EchoWebSocketHandler(s, [], [])
        cherrypy.engine.publish('handle-websocket', h, ('127.0.0.1', 0))
        self.assertEquals(len(cherrypy.engine.websocket.handlers), 1)
        self.assertTrue(cherrypy.engine.websocket.handlers[0][0] is h)
        self.assertEquals(cherrypy.engine.websocket.handlers[0][1], ('127.0.0.1', 0))

        self.assertEquals(len(cherrypy.engine.websocket.handlers), 1)
        h.close() # shutdown server side of the websocket connection
        h.client_terminated = True # we aren't actually connected so pretend the client shutdown
        cherrypy.engine.publish('main')
        self.assertEquals(len(cherrypy.engine.websocket.handlers), 0)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [CherryPyTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
