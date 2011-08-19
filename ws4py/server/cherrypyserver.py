# -*- coding: utf-8 -*-
import base64
from hashlib import sha1
import inspect
import socket
import time
import threading
import traceback
from sys import exc_info

import cherrypy
from cherrypy import Tool
from cherrypy.process import plugins
from cherrypy.wsgiserver import HTTPConnection, HTTPRequest

from ws4py import WS_KEY
from ws4py.streaming import Stream

__all__ = ['WebSocketTool', 'WebSocketPlugin', 'WebSocketHandler']

class WebSocketHandler(object):
    def __init__(self, sock, protocols, extensions):
        self.stream = Stream()
        
        self.protocols = protocols
        self.extensions = extensions

        self.sock = sock
        self.sock.settimeout(30.0)
        
        self.client_terminated = False
        self.server_terminated = False

        self._lock = threading.Lock()
        self._th = threading.Thread(target=self._receive)

    def opened(self):
        self._th.start()

    def close(self, code=1000, reason=''):
        if not self.server_terminated:
            self.server_terminated = True
            print "burp", code
            self.sock.sendall(self.stream.close(code=code, reason=reason))
            
    def closed(self, code, reason):
        pass

    def received_message(self, m):
        self.send(str(m), m.is_binary)
    
    @property
    def terminated(self):
        return self.client_terminated is True and self.server_terminated is True
    
    def write_to_connection(self, bytes):
        return self.sock.sendall(bytes)

    def read_from_connection(self, amount):
        return self.sock.recv(amount)
        
    def close_connection(self):
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except:
                pass

    def ponged(self, pong):
        pass

    def send(self, payload, binary=False):
        if isinstance(payload, basestring):
            if not binary:
                self.write_to_connection(self.stream.text_message(payload).single())
            else:
                self.write_to_connection(self.stream.binary_message(payload).single())
                
        elif type(payload) == types.GeneratorType:
            bytes = payload.next()
            first = True
            for chunk in payload:
                if not binary:
                    self.write_to_connection(self.stream.text_message(bytes).fragment(first=first))
                else:
                    self.write_to_connection(self.stream.binary_message(payload).fragment(first=first))
                bytes = chunk
                first = False
            if not binary:
                self.write_to_connection(self.stream.text_message(bytes).fragment(last=True))
            else:
                self.write_to_connection(self.stream.text_message(bytes).fragment(last=True))

    def _receive(self):
        next_size = 2
        try:
            while not self.terminated:
                bytes = self.sock.recv(next_size)
                if not bytes:
                    raise IOError()
                
                with self._lock:
                    s = self.stream
                    next_size = s.parser.send(bytes)

                    if s.closing:
                        print s.closing
                        if not self.server_terminated:
                            next_size = 2
                            self.close()
                        else:
                            self.client_terminated = True
                            self.close_connection()
                            self.closed(s.closing.code, s.closing.reason)

                    elif s.errors:
                        errors = s.errors[:]
                        for error in s.errors:
                            print error.code, error.reason
                            self.close(error.code, error.reason)
                            s.errors.remove(error)
                        self.close_connection()
                            
                    elif s.has_messages:
                        self.received_message(s.messages.pop())

                    for ping in s.pings:
                        self.sock.sendall(s.pong(str(ping.data)))
                    s.pings = []

                    for pong in s.pongs:
                        self.ponged(pong)
                    s.pongs = []
                    

        except IOError:
            self.client_terminated = True
            self.server_terminated = True
        except:
            print "".join(traceback.format_exception(*exc_info()))
            self.client_terminated = True
            self.server_terminated = True
            raise
        finally:
            self.close_connection()

class WebSocketTool(Tool):
    def __init__(self):
        Tool.__init__(self, 'before_request_body', self.upgrade)

    def _setup(self):
        conf = self._merged_args()
        hooks = cherrypy.serving.request.hooks
        p = conf.pop("priority", getattr(self.callable, "priority",
                                         self._priority))
        hooks.attach(self._point, self.callable, priority=p, **conf)
        hooks.attach('before_finalize', self.complete,
                     priority=p)
        hooks.attach('on_end_resource', self.cleanup_headers,
                     priority=70)
        hooks.attach('on_end_request', self.start_handler,
                     priority=70)

    def upgrade(self, protocols=None, extensions=None, version=8, handler_cls=WebSocketHandler):
        """
        Performs the upgrade of the connection to the WebSocket
        protocol.

        The provided protocols may be a list of WebSocket
        protocols supported by the instance of the tool.

        When no list is provided and no protocol is either
        during the upgrade, then the protocol parameter is
        not taken into account. On the other hand,
        if the protocol from the handshake isn't part
        of the provided list, the upgrade fails immediatly.
        """
        request = cherrypy.serving.request
        request.process_request_body = False
        
        ws_protocols = None
        ws_location = None
        ws_version = 8
        ws_key = None
        ws_extensions = []
        
        if request.method != 'GET':
            raise HandshakeError('Method is not GET')

        for key, expected_value in [('Upgrade', 'websocket'),
                                     ('Connection', 'Upgrade')]:
            actual_value = request.headers.get(key)
            if not actual_value:
                raise HandshakeError('Header %s is not defined' % key)
            if expected_value and actual_value != expected_value:
                raise HandshakeError('Illegal value for header %s: %s' %
                                     (key, actual_value))
            
        key = request.headers.get('Sec-WebSocket-Key')
        if key:
            ws_key = base64.b64decode(key)
            if len(ws_key) != 16:
                raise HandshakeError("WebSocket key's length is invalid")
        
        version = request.headers.get('Sec-WebSocket-Version')
        if version:
            if version != str(ws_version):
                raise HandshakeError('Unsupported WebSocket version')
        else:
            raise HandshakeError('WebSocket version required')
        
        protocols = protocols or []
        subprotocols = request.headers.get('Sec-WebSocket-Protocol')
        if subprotocols:
            ws_protocols = []
            for s in subprotocols.split(','):
                s = s.strip()
                if s in protocols:
                    ws_protocols.append(s)

        exts = extensions or []
        extensions = request.headers.get('Sec-WebSocket-Extensions')
        if extensions:
            for ext in extensions.split(','):
                ext = ext.strip()
                if ext in exts:
                    ws_extensions.append(ext)
        
        location = []
        include_port = False
        if request.scheme == "https":
            location.append("wss://")
            include_port = request.local.port != 443
        else:
            location.append("ws://")
            include_port = request.local.port != 80
        location.append('localhost')
        if include_port:
            location.append(":%d" % request.local.port)
        location.append(request.path_info)
        if request.query_string != "":
            location.append("?%s" % request.query_string)
        ws_location = ''.join(location)

        
        response = cherrypy.serving.response
        response.stream = True
        response.status = '101 Switching Protocols'
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Upgrade'] = 'websocket'
        response.headers['Connection'] = 'Upgrade'
        response.headers['Sec-WebSocket-Version'] = str(ws_version)
        response.headers['Sec-WebSocket-Accept'] = base64.b64encode(sha1(key + WS_KEY).digest())
        if ws_protocols:
            response.headers['Sec-WebSocket-Protocol'] = ', '.join(ws_protocols)
        if ws_extensions:
            response.headers['Sec-WebSocket-Extensions'] = ','.join(ws_extensions)

        cherrypy.log("Managing WebSocket connection from %s:%d" % (request.remote.ip,
                                                                   request.remote.port))
        sock = request.rfile.rfile._sock
        # By creating a new object, we avoid keeping
        # track of the whole CherryPy's stack once the
        # upgrade is finished and the socket is
        # handed over
        ws_conn = socket.fromfd(sock.fileno(), sock.family,
                                sock.type, sock.proto)
        request.ws_handler = handler_cls(ws_conn, ws_protocols, ws_extensions)
        cherrypy.engine.publish('handle-websocket', request.ws_handler)
        
    def complete(self):
        self._set_internal_flags()

    def cleanup_headers(self):
        response = cherrypy.response
        headers = response.header_list[:]
        for (k, v) in headers:
            if k.startswith('Sec-Web'):
                response.header_list.remove((k, v))
                response.header_list.append((k.replace('Sec-Websocket', 'Sec-WebSocket'), v))

    def start_handler(self):
        request = cherrypy.request
        request.ws_handler.opened()
        request.ws_handler = None
        
    def _set_internal_flags(self):
        """
        CherryPy has two internal flags that we are interested in
        to enable WebSocket within the server. They can't be set via
        a public API and considering I'd want to make this extension
        as compatible as possible whilst refraining in exposing more
        than should be within CherryPy, I prefer performing a bit
        of introspection to set those flags. Even by Python standards
        such introspection isn't the cleanest but it works well
        enough in this case.

        This also means that we do that only on WebSocket
        connections rather than globally and therefore we do not
        harm the rest of the HTTP server.
        """
        current = inspect.currentframe()
        while True:
            if not current:
                break
            _locals = current.f_locals
            if 'self' in _locals:
               if type(_locals['self']) == HTTPRequest:
                   _locals['self'].close_connection = True
               if type(_locals['self']) == HTTPConnection:
                   _locals['self'].linger = True
                   # HTTPConnection is more inner than
                   # HTTPRequest so we can leave once
                   # we're done here
                   return
            _locals = None
            current = current.f_back

class WebSocketPlugin(plugins.SimplePlugin):
    def __init__(self, bus):
        plugins.SimplePlugin.__init__(self, bus)
        self.handlers = []

    def start(self):
        cherrypy.log("Starting WebSocket processing")
        self.bus.subscribe('handle-websocket', self.handle)
        self.bus.subscribe('main', self.cleanup)
        
    def stop(self):
        cherrypy.log("Terminating WebSocket processing")
        self.bus.unsubscribe('main', self.cleanup)
        self.bus.unsubscribe('handle-websocket', self.handle)

        for handler in self.handlers:
            handler.close()

    def handle(self, ws_handler):
        self.handlers.append(ws_handler)

    def cleanup(self):
        handlers = self.handlers[:]
        for handler in handlers:
            if handler.terminated:
                handler.close_connection()
                handler._th.join()
                self.handlers.remove(handler)
                

if __name__ == '__main__':
    import random
    
    cherrypy.config.update({'server.socket_host': '127.0.0.1',
                            'server.socket_port': 9000})
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()
    
    class Root(object):
        @cherrypy.expose
        @cherrypy.tools.websocket(on=False)
        def ws(self):
            return """<html>
        <head>
          <script type='application/javascript' src='https://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js'> </script>
          <script type='application/javascript'>
            $(document).ready(function() {
              var ws = new WebSocket('ws://192.168.0.10:8888/');
              ws.onmessage = function (evt) {
                 $('#chat').val($('#chat').val() + evt.data + '\\n');                  
              };
              ws.onopen = function() {
                 ws.send("Hello there");
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
        def index(self):
            pass
        
    cherrypy.quickstart(Root(), '/', config={'/': {'tools.websocket.on': True}})
