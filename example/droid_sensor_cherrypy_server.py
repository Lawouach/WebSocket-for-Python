# -*- coding: utf-8 -*-
from __future__ import print_function
import os.path
import cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket

class BroadcastWebSocketHandler(WebSocket):
    def received_message(self, m):
        cherrypy.engine.publish('websocket-broadcast', str(m))
        
class Root(object):
    @cherrypy.expose
    def display(self):
        return """<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <title>WebSocket example displaying Android device sensors</title>
      <link rel="stylesheet" href="/css/style.css" type="text/css" />

      <script type='application/javascript' src='http://code.jquery.com/jquery-1.9.1.min.js'></script>
      <script type="application/javascript" src="http://calebevans.me/projects/jcanvas/resources/jcanvas/jcanvas.min.js"> </script>
      <script type="application/javascript" src="/js/droidsensor.js"> </script>
      <script type="application/javascript">
        $(document).ready(function() {
          initWebSocket();
          drawAll();
        });
      </script>
    </head>
    <body>
    <section id="content" class="body">
    <canvas id="canvas" width="900" height="620"></canvas>
    </section>
    </body>
    </html>
    """

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))

    @cherrypy.expose
    def index(self):
        return """<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <title>WebSocket example displaying Android device sensors</title>

      <script type='application/javascript' src='http://code.jquery.com/jquery-1.9.1.min.js'></script>
      <script type="application/javascript" src="/js/droidsensor.js"> </script>
      <script type="application/javascript">
        $(document).ready(function() {
          initWebSocketAndSensors();
        });
      </script>
    </head>
    <body>
    </body>
    </html>
    """
        
if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 9000,
        'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
        }
    )
    print(os.path.abspath(os.path.join(__file__, 'static')))
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.quickstart(Root(), '', config={
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'js'
            },
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'css'
            },
        '/images': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'images'
            },
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': BroadcastWebSocketHandler
            }
        }
    )
