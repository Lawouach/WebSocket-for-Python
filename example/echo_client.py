# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient

class EchoClient(WebSocketClient):
    def opened(self, protocols, extensions):
        def data_provider():
            for i in range(1, 200, 25):
                yield "#" * i
                
        self.send(data_provider())
            
        for i in range(0, 200, 25):
            self.send("*" * i)

    def received_message(self, m):
        print m, len(str(m))
        if len(str(m)) == 175:
            self.close()

if __name__ == '__main__':
    try:
        ws = EchoClient('http://localhost:9000/ws', protocols=['http-only', 'chat'])
        ws.connect()
    except KeyboardInterrupt:
        ws.close()
