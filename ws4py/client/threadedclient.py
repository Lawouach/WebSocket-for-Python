# -*- coding: utf-8 -*-
import threading

from ws4py.client import WebSocketBaseClient

__all__ = ['WebSocketClient']

class WebSocketClient(WebSocketBaseClient):
    def __init__(self, url, protocols=None, extensions=None):
        WebSocketBaseClient.__init__(self, url, protocols, extensions)
        self._th = threading.Thread(target=self.run, name='WebSocketClient')
        self._th.daemon = True

    @property
    def daemon(self):
        return self._th.daemon

    @daemon.setter
    def daemon(self, flag):
        self._th.daemon = flag

    def handshake_ok(self):
        self._th.start()
        self._th.join(timeout=1.0)

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
                self.close(reason="Done...")

    ws = MyClient('ws://localhost:9000/ws', protocols=['http-only', 'chat'])
    try:
        ws.connect()
    except (KeyboardInterrupt, SystemExit):
        ws.close()
