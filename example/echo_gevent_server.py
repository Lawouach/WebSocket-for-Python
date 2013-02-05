# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()

import argparse
import random
import os

import gevent
import gevent.pywsgi

from ws4py.server.geventserver import WebSocketWSGIApplication, \
     WebSocketWSGIHandler, WSGIServer
from ws4py.websocket import EchoWebSocket

class BroadcastWebSocket(EchoWebSocket):
    def opened(self):
        app = self.environ['ws4py.app']
        app.clients.append(self)

    def received_message(self, m):
        # self.clients is set from within the server
        # and holds the list of all connected servers
        # we can dispatch to
        app = self.environ['ws4py.app']
        for client in app.clients:
            client.send(m)

    def closed(self, code, reason="A client left the room without a proper explanation."):
        app = self.environ.pop('ws4py.app')
        if self in app.clients:
            app.clients.remove(self)
            for client in app.clients:
                try:
                    client.send(reason)
                except:
                    pass

class EchoWebSocketApplication(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ws = WebSocketWSGIApplication(handler_cls=BroadcastWebSocket)

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
            environ['ws4py.app'] = self
            return self.ws(environ, start_response)

        return self.webapp(environ, start_response)

    def favicon(self, environ, start_response):
        """
        Don't care about favicon, let's send nothing.
        """
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return ""

    def webapp(self, environ, start_response):
        """
        Our main webapp that'll display the chat form
        """
        status = '200 OK'
        headers = [('Content-type', 'text/html')]

        start_response(status, headers)

        return """<html>
        <head>
        <script type='application/javascript' src='https://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js'></script>
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

              window.onbeforeunload = function(e) {
                 $('#chat').val($('#chat').val() + 'Bye bye...\\n');
                 ws.close(1000, '%(username)s left the room');

                 if(!e) e = window.event;
                 e.stopPropagation();
                 e.preventDefault();
              };
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
    from ws4py import configure_logger
    configure_logger()

    parser = argparse.ArgumentParser(description='Echo gevent Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    args = parser.parse_args()

    server = WSGIServer((args.host, args.port), EchoWebSocketApplication(args.host, args.port))
    server.serve_forever()
