from ws4py import configure_logger
from ws4py.websocket import WebSocket
from ws4py.messaging import Message, TextMessage

logger = configure_logger(stdout=True)

class DataSource(object):
    def __init__(self):
        self.frames = set()
        self.frame = None
        self.remaining_bytes = None

    def setblocking(self, flag):
        pass

    def feed(self, message):
        if isinstance(message, Message):
            message = message.single(mask=True)
        else:
            message = TextMessage(message).single(mask=True)
        self.frames.add(message)

    def recv(self, size):
        if not self.frame:
            if not self.frames:
                return b''
            self.frame = self.frames.pop()
            self.remaining_bytes = self.frame

        current_bytes = self.remaining_bytes[:size]
        self.remaining_bytes = self.remaining_bytes[size:]

        if self.remaining_bytes is b'':
            self.frame = None
            self.remaining_bytes = None

        return current_bytes

class LogWebSocket(WebSocket):
    def opened(self):
        logger.info("WebSocket now ready")

    def closed(self, code=1000, reason="Burp, done!"):
        logger.info("Terminated with reason '%s'" % reason)

    def received_message(self, m):
        logger.info("Received message: %s" % m)

if __name__ == '__main__':
    source = DataSource()
    ws = LogWebSocket(sock=source)

    source.feed(u'hello there')
    source.feed(u'a bit more')

    ws.run()
