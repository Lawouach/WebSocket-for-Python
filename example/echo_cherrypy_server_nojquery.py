# -*- coding: utf-8 -*-
import argparse
import random
import os

import cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

class ChatWebSocketHandler(WebSocket):
    def received_message(self, m):
        cherrypy.engine.publish('websocket-broadcast', m)

    def closed(self, code, reason="A client left the room without a proper explanation."):
        cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))

class Root(object):
    def __init__(self, host, port, ssl=False):
        self.host = host
        self.port = port
        self.scheme = 'wss' if ssl else 'ws'

    @cherrypy.expose
    def index(self):
        return """<html>
    <head>
    </head>
    <body>
    <p>Note: If viewing this as localhost via SSL and it doesn't work, try using 127.0.0.1 directly</p>
    <div>
      <textarea id='chat' cols='35' rows='10'></textarea>
      <br />
      <label for='message'>%(username)s: </label><input id='message' />
      <button type="button" id='send' >Send</button>
      </div>
           <script type='application/javascript'>
               websocket = '%(scheme)s://%(host)s:%(port)s/ws';
               if (window.WebSocket) {
                 ws = new WebSocket(websocket);
               }
               else if (window.MozWebSocket) {
                 ws = MozWebSocket(websocket);
               }
               else {
                 console.log('WebSocket Not Supported');
               }
               var c = document.getElementById('chat');

               window.onbeforeunload = function(e) {
                 c.value=c.value + 'Bye bye...\\n';
                 ws.close(1000, '%(username)s left the room');

                 if(!e) e = window.event;
                 e.stopPropagation();
                 e.preventDefault();
               };
               ws.onmessage = function (evt) {
                      c.value=c.value + evt.data + '\\n';
               };
               ws.onopen = function() {
                  ws.send("%(username)s entered the room");
               };
               ws.onclose = function(evt) {
                      c.value=c.value + 'Connection closed by server: ' + evt.code + ' \"' + evt.reason + '\"\\n';
               };

              document.getElementById('send').onclick = function() {
                  console.log(document.getElementById('message').value);
                  ws.send("%(username)s: " +document.getElementById('message').value);
                   document.getElementById('message').value ="";
                  return false;
               };


           </script>
    </body>
    </html>
    """ % {'username': "User%d" % random.randint(0, 100), 'host': self.host, 'port': self.port, 'scheme': self.scheme}

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))

if __name__ == '__main__':
    import logging
    from ws4py import configure_logger
    configure_logger(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Echo CherryPy Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    parser.add_argument('--ssl', action='store_true')
    args = parser.parse_args()

    cherrypy.config.update({'server.socket_host': args.host,
                            'server.socket_port': args.port,
                            'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))})

    if args.ssl:
        cherrypy.config.update({
        'server.ssl_module':'builtin',
'server.ssl_certificate': 'server.crt',
                                'server.ssl_private_key': 'server.key'})

    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.quickstart(Root(args.host, args.port, args.ssl), '', config={
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
