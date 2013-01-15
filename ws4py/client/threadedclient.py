# -*- coding: utf-8 -*-
import threading

from ws4py.client import WebSocketBaseClient

__all__ = ['WebSocketClient']

class WebSocketClient(WebSocketBaseClient):
    def __init__(self, url, protocols=None, extensions=None, heartbeat_freq=None):
        WebSocketBaseClient.__init__(self, url, protocols, extensions, heartbeat_freq)
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
