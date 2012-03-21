# -*- coding: utf-8 -*-
import gevent
import gevent.pywsgi
from gevent import version_info
IS_GEVENT_V10 = version_info[0] == 1
del version_info

from ws4py.server.wsgi.middleware import WebSocketUpgradeMiddleware
from ws4py.websocket import WebSocket

class UpgradableWSGIHandler(gevent.pywsgi.WSGIHandler):
    """Upgradable version of gevent.pywsgi.WSGIHandler class
    
    This is a drop-in replacement for gevent.pywsgi.WSGIHandler that supports
    protocol upgrades via WSGI environment. This means you can create upgraders
    as WSGI apps or WSGI middleware.
    
    If an HTTP request comes in that includes the Upgrade header, it will add
    to the environment two items:
    
    ``upgrade.protocol` `
      The protocol to upgrade to. Checking for this lets you know the request
      wants to be upgraded and the WSGI server supports this interface. 
    
    ``upgrade.socket``
      The raw Python socket object for the connection. From this you can do any
      upgrade negotiation and hand it off to the proper protocol handler.
    
    The upgrade must be signalled by starting a response using the 101 status
    code. This will inform the server to flush the headers and response status
    immediately, not to expect the normal WSGI app return value, and not to 
    look for more HTTP requests on this connection. 
    
    To use this handler with gevent.pywsgi.WSGIServer, you can pass it to the
    constructor:
    
    .. code-block:: python
       :linenos:

       server = WSGIServer(('127.0.0.1', 80), app, 
                           handler_class=UpgradableWSGIHandler)
    
    Alternatively, you can specify it as a class variable for a WSGIServer 
    subclass:
    
    .. code-block:: python
       :linenos:

       class UpgradableWSGIServer(gevent.pywsgi.WSGIServer):
             handler_class = UpgradableWSGIHandler
    
    """
    def run_application(self):
        upgrade_header = self.environ.get('HTTP_UPGRADE', '').lower()
        if upgrade_header:
            self.environ['upgrade.protocol'] = upgrade_header
            self.environ['upgrade.socket'] = self.socket
            def start_response_for_upgrade(status, headers, exc_info=None):
                write = self.start_response(status, headers, exc_info)
                if self.code == 101:
                    # flushes headers now
                    if IS_GEVENT_V10:
                        self.headers_sent = True

                        sline = '%s %s\r\n' % (self.request_version, self.status)
                        write(sline)
                        self.response_length += len(sline)
                        
                        for header in headers:
                            hline = '%s: %s\r\n' % header
                            write(hline)
                            self.response_length += len(hline)
                            
                        write('\r\n')
                        self.response_length += 2
                    else:
                        towrite = ['%s %s\r\n' % (self.request_version, self.status)]
                        for header in headers:
                            towrite.append('%s: %s\r\n' % header)
                        towrite.append('\r\n')
                        self.wfile.writelines(towrite)
                        self.response_length += sum(len(x) for x in towrite)
                return write
            try:
                self.result = self.application(self.environ, start_response_for_upgrade)
                if self.code != 101:
                    self.process_result()
            finally:
                if hasattr(self, 'code') and self.code == 101:
                    self.rfile.close() # makes sure we stop processing requests
        else:
            gevent.pywsgi.WSGIHandler.run_application(self)

class WebSocketServer(gevent.pywsgi.WSGIServer):
    handler_class = UpgradableWSGIHandler
    
    def __init__(self, address, *args, **kwargs):
        protocols = kwargs.pop('websocket_protocols', [])
        extensions = kwargs.pop('websocket_extensions', [])
        websocket = kwargs.pop('websocket_class', WebSocket)
        
        gevent.pywsgi.WSGIServer.__init__(self, address, *args, **kwargs)
        self.application = WebSocketUpgradeMiddleware(app=self.handler,
                                                      protocols=protocols,
                                                      extensions=extensions,
                                                      websocket_class=websocket)    

    def handler(self, websocket):
        g = gevent.spawn(websocket.run)
        g.join()
        return ['']

if __name__ == '__main__':
    import logging
    import sys
    logging.basicConfig(format='%(asctime)s %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    h = logging.StreamHandler()
    h.setLevel(logging.DEBUG)
    logger.addHandler(h)

    from ws4py.websocket import EchoWebSocket
    server = WebSocketServer(('127.0.0.1', 9001), websocket_class=EchoWebSocket)
    server.serve_forever()
        
