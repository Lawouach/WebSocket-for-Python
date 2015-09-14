def run_threaded():
    from ws4py.client.threadedclient import WebSocketClient
    class EchoClient(WebSocketClient):
        def opened(self):
            self.send("hello")
            
        def closed(self, code, reason=None):
            print(("Closed down", code, reason))

        def received_message(self, m):
            print(m)
            self.close()
            
    try:
        ws = EchoClient('wss://localhost:9000/ws')
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()

def run_tornado():
    from tornado import ioloop
    from ws4py.client.tornadoclient import TornadoWebSocketClient
    class MyClient(TornadoWebSocketClient):
        def opened(self):
            self.send("hello")
            
        def closed(self, code, reason=None):
            print(("Closed down", code, reason))
            ioloop.IOLoop.instance().stop()

        def received_message(self, m):
            print(m)
            self.close()

    ws = MyClient('wss://localhost:9000/ws')
    ws.connect()

    ioloop.IOLoop.instance().start()

def run_gevent():
    from gevent import monkey; monkey.patch_all()
    import gevent
    from ws4py.client.geventclient import WebSocketClient
    
    ws = WebSocketClient('wss://localhost:9000/ws')
    ws.connect()

    ws.send("hello")
    
    def incoming():
        while True:
            m = ws.receive()
            if m is not None:
                print(m)
            else:
                break
            
        ws.close()

    gevent.joinall([gevent.spawn(incoming)])

#run_gevent()
run_threaded()
run_tornado()
