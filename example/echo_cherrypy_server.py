# -*- coding: utf-8 -*-
import argparse
import random
import os

import cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.server.handler.threadedhandler import WebSocketHandler, EchoWebSocketHandler

class ChatWebSocketHandler(WebSocketHandler):
    def received_message(self, m):
        cherrypy.engine.publish('websocket-broadcast', str(m))

class Root(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @cherrypy.expose
    def index(self):
        return """<html>
    <head>
      <script type='application/javascript' src='/js/jquery-1.6.2.min.js'></script>
      <script type='application/javascript'>
        $(document).ready(function() {

          websocket = 'ws://%(host)s:%(port)s/ws';
          if (window.WebSocket) {
            ws = WebSocket(websocket);
          }
          else if (window.MozWebSocket) {
            ws = MozWebSocket(websocket);
          }
          else {
            console.log('WebSocket Not Supported');
            return;
          }

          $(window).unload(function() {
             ws.close();
          });
          ws.onmessage = function (evt) {
             $('#chat').val($('#chat').val() + evt.data + '\\n');
          };
          ws.onopen = function() {
             ws.send("%(username)s entered the room");
          };

          $('#send').click(function() {
             console.log($('#message').val());
             ws.send('%(username)s: ' + $('#message').val());
             $('#message').val("");
             return false;
          });
        });
      </script>
    </head>
    <body>
    <form action='#' id='chatform' method='get'>
      <textarea id='chat' cols='35' rows='10'></textarea>
      <br />
      <label for='message'>%(username)s: </label><input type='text' id='message' />
      <input id='send' type='submit' value='Send' />
      </form>
    </body>
    </html>
    """ % {'username': "User%d" % random.randint(0, 100),
           'host': self.host,
           'port': self.port}

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Echo CherryPy Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    args = parser.parse_args()

    cherrypy.config.update({'server.socket_host': args.host,
                            'server.socket_port': args.port,
                            'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))})

    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.quickstart(Root(args.host, args.port), '', config={
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': ChatWebSocketHandler
            },
        '/js': {
              'tools.staticdir.on': True,
              'tools.staticdir.dir': 'js'
            }
        }
    )
