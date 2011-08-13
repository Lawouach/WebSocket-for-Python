# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
from tornado.websocket import WebSocketHandler

class EchoWebSocket(WebSocketHandler):
    def open(self):
        print "WebSocket opened"
        
    def on_message(self, message):
        print message
        self.write_message("You said %s" % message)
            
    def on_close(self):
        print "WebSocket closed"
              
if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", EchoWebSocket),
    ])
    application.listen(8888, address="192.168.0.10")
    tornado.ioloop.IOLoop.instance().start()
