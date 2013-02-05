# -*- coding: utf-8 -*-
import logging
import select
import threading
import time

from ws4py import format_addresses

logger = logging.getLogger('ws4py')

class SelectPoller(object):
    def __init__(self, timeout=0.1):
        self._fds = []
        self.timeout = timeout

    def release(self):
        self._fds = []

    def register(self, fd):
        if fd not in self._fds:
            self._fds.append(fd)

    def unregister(self, fd):
        if fd in self._fds:
            self._fds.remove(fd)

    def poll(self):
        r, w, x = select.select(self._fds, [], [], self.timeout)
        return r

class EPollPoller(object):
    def __init__(self, timeout=0.1):
        self.poller = select.epoll()
        self.timeout = timeout

    def release(self):
        self.poller.close()

    def release(self):
        self.poller.close()

    def register(self, fd):
        try:
            self.poller.register(fd, select.EPOLLIN | select.EPOLLPRI)
        except IOError:
            pass

    def unregister(self, fd):
        self.poller.unregister(fd)

    def poll(self):
        events = self.poller.poll(timeout=self.timeout)
        for fd, event in events:
            if event | select.EPOLLIN | select.EPOLLPRI:
                yield fd

class WebSocketManager(threading.Thread):
    def __init__(self, poller=None):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.websockets = {}

        if hasattr(select, "epoll"):
            self.poller = EPollPoller()
            logger.info("Using epoll")
        else:
            self.poller = SelectPoller()
            logger.info("Using select as epoll is not available")

    def __len__(self):
        return len(self.websockets)

    def add(self, websocket):
        logger.info("Managing websocket %s" % format_addresses(websocket))
        websocket.opened()
        with self.lock:
            fd = websocket.sock.fileno()
            self.websockets[fd] = websocket
            self.poller.register(fd)

    def remove(self, websocket):
        logger.info("Removing websocket %s" % format_addresses(websocket))
        with self.lock:
            fd = websocket.sock.fileno()
            self.websockets.pop(fd)
            self.poller.unregister(fd)

    def stop(self):
        self.running = False
        with self.lock:
            self.websockets.clear()
            self.poller.release()

    def run(self):
        self.running = True
        while self.running:
            with self.lock:
                polled = self.poller.poll()

            if not self.running:
                break

            for fd in polled:
                if not self.running:
                    break

                ws = self.websockets.get(fd)

                if ws:
                    if not ws.terminated and not ws.once():
                        with self.lock:
                            fd = ws.sock.fileno()
                            self.websockets.pop(fd)
                            self.poller.unregister(fd)

                        if not ws.terminated:
                            logger.info("Terminating websocket %s" % format_addresses(ws))
                            ws.terminate()

    def close_all(self, code=1001, message='Server is shutting down'):
        with self.lock:
            logger.info("Closing all websockets with [%d] '%s'" % (code, message))
            for ws in self.websockets.itervalues():
                ws.close(code=1001, reason=message)

    def broadcast(self, message, binary=False):
        with self.lock:
            websockets = self.websockets.copy()

        for ws in websockets.itervalues():
            if not ws.terminated:
                try:
                    ws.send(message, binary)
                except Exception, ex:
                    pass
