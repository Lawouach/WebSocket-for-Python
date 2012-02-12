# -*- coding: utf-8 -*-
from multiprocessing import Process

def run_cherrypy_server(host="127.0.0.1", port=9000):
    from gevent import monkey; monkey.patch_all()
    import cherrypy
    
    from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
    from ws4py.websocket import EchoWebSocket
    
    cherrypy.config.update({'server.socket_host': host,
                            'server.socket_port': port,
                            'log.screen': False})
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    class Root(object):
        @cherrypy.expose
        def index(self):
            pass

    config = {
        '/': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': EchoWebSocket
            }
        }
    cherrypy.quickstart(Root(), '/', config)

def run_gevent_server(host="127.0.0.1", port=9001):
    from gevent import monkey; monkey.patch_all()
    from ws4py.server.geventserver import WebSocketServer
    from ws4py.websocket import EchoWebSocket
    
    server = WebSocketServer((host, port), websocket_class=EchoWebSocket)
    server.serve_forever()

if __name__ == '__main__':
    p0 = Process(target=run_cherrypy_server)
    p0.daemon = True
    p0.start()
    
    p1 = Process(target=run_gevent_server)
    p1.daemon = True
    p1.start()
    
    p0.join()
    p1.join()
