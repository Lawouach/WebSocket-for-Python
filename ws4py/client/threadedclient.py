# -*- coding: utf-8 -*-
import threading

from ws4py.client import WebSocketBaseClient

__all__ = ['WebSocketClient']

class WebSocketClient(WebSocketBaseClient):
    def __init__(self, url, protocols=None, extensions=None, daemon=False):
        WebSocketBaseClient.__init__(self, url, protocols, extensions)
        self._th = threading.Thread(target=self.run, name='WebSocketClient')
        self._th.daemon = daemon
        
    def handshake_ok(self):
        self._th.start()
        self._th.join()
        
if __name__ == '__main__':
    class MyClient(WebSocketClient):
        def opened(self):
            def data_provider():
                for i in range(1, 200, 25):
                    yield "#" * i

            self.send(data_provider())
            
            for i in range(0, 200, 25):
                self.send("*" * i)

        def closed(self, code, reason=None):
            print code, reason
            
        def received_message(self, m):
            print m, len(str(m))
            if len(str(m)) == 175:
                self.close()

    try:
        ws = MyClient('http://localhost:9000/ws', protocols=['http-only', 'chat'])
        ws.connect()
    except KeyboardInterrupt:
        ws.close()

        print "terminated"
