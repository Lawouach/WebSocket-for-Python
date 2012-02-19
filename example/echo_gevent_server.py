# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()

import argparse
import random
import os

import gevent
import gevent.pywsgi

from ws4py.server.geventserver import UpgradableWSGIHandler
from ws4py.server.wsgi.middleware import WebSocketUpgradeMiddleware
from ws4py.websocket import EchoWebSocket

class EchoWebSocketServer(gevent.pywsgi.WSGIServer):
    handler_class = UpgradableWSGIHandler
    
    def __init__(self, host, port):
        gevent.pywsgi.WSGIServer.__init__(self, (host, port))
        
        self.host = host
        self.port = port

        self.application = self
        
        # let's use wrap the websocket handler with
        # a middleware that'll perform the websocket
        # handshake
        self.ws = WebSocketUpgradeMiddleware(app=self.ws_app,
                                             websocket_class=EchoWebSocket)

        # keep track of connected websocket clients
        # so that we can brodcasts messages sent by one
        # to all of them. Aren't we cool?
        self.clients = []

    def __call__(self, environ, start_response):
        """
        Good ol' WSGI application. This is a simple demo
        so I tried to stay away from dependencies.
        """
        if environ['PATH_INFO'] == '/favicon.ico':
            return self.favicon(environ, start_response)
        
        if environ['PATH_INFO'] == '/ws':
            return self.ws(environ, start_response)
        
        if environ['PATH_INFO'].startswith('/js'):
            return self.static(environ, start_response)
        
        return self.webapp(environ, start_response)

    def ws_app(self, websocket):
        g = gevent.spawn(websocket.run)
        g.start()
        g.join()

    def favicon(self, environ, start_response):
        """
        Don't care about favicon, let's send nothing.
        """
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return ""

    def static(self, environ, start_response):
        """
        Not the sexiest static handler but does the job
        for the demo
        """
        path = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                             './static/%s' % environ['PATH_INFO']))
        if not os.path.exists(path):
            status = '404 Not Found'
            headers = [('Content-type', 'text/plain')]
            return ""
        
        status = '200 OK'
        headers = [('Content-type', 'text/javascript')]
        
        start_response(status, headers)
        
        return file(path).read()
        
    def webapp(self, environ, start_response):
        """
        Our main webapp that'll display the chat form
        """
        status = '200 OK'
        headers = [('Content-type', 'text/html')]

        start_response(status, headers)

        return """<html>
        <head>
          <script type='application/javascript' src='/js/jquery-1.6.2.min.js'></script>
          <script type='application/javascript'>
            $(document).ready(function() {

              websocket = 'ws://%(host)s:%(port)s/ws';
              if (window.WebSocket) {
                ws = new WebSocket(websocket);
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
              ws.onclose = function(evt) {
                 $('#chat').val($('#chat').val() + 'Connection closed by server: ' + evt.code + ' \"' + evt.reason + '\"\\n');  
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Echo gevent Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    args = parser.parse_args()

    server = EchoWebSocketServer(args.host, args.port)
    server.serve_forever()
    
