# -*- coding: utf-8 -*-
import random

import cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.server.handler.threadedhandler import WebSocketHandler, EchoWebSocketHandler

class ChatWebSocketHandler(WebSocketHandler):
    def received_message(self, m):
        cherrypy.engine.publish('websocket-broadcast', str(m))
        
class Root(object):
    @cherrypy.expose
    def index(self):
        return """<html>
    <head>
      <script type='application/javascript' src='https://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js'> </script>
      <script type='application/javascript'>
        $(document).ready(function() {
          var ws = new WebSocket('ws://localhost:9000/ws');
          $(window).unload(function() {
             ws.close();
          });
          ws.onmessage = function (evt) {
             $('#chat').val($('#chat').val() + evt.data + '\\n');                  
          };
          ws.onopen = function() {
             ws.send("%(username)s entered the room");
          };
          $('#chatform').submit(function() {
             ws.send('%(username)s: ' + $('#message').val());
             $('#message').val("");
             return false;
          });
        });
      </script>
    </head>
    <body>
    <form action='/echo' id='chatform' method='get'>
      <textarea id='chat' cols='35' rows='10'></textarea>
      <br />
      <label for='message'>%(username)s: </label><input type='text' id='message' />
      <input type='submit' value='Send' />
      </form>
    </body>
    </html>
    """ % {'username': "User%d" % random.randint(0, 100)}

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': 9000})
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.quickstart(Root(), '', config={
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': ChatWebSocketHandler
            }
        }
    )
