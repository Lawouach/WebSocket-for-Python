# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()

import gevent
from ws4py.client.geventclient import WebSocketClient

if __name__ == '__main__':
    ws = WebSocketClient('ws://localhost:9000/ws', protocols=['http-only', 'chat'])
    ws.connect()

    ws.send("Hello world")
    print((ws.receive(),))

    ws.send("Hello world again")
    print((ws.receive(),))

    def incoming():
        while True:
            m = ws.receive()
            if m is not None:
                m = str(m)
                print((m, len(m)))
                if len(m) == 35:
                    ws.close()
                    break
            else:
                break
        print(("Connection closed!",))

    def outgoing():
        for i in range(0, 40, 5):
            ws.send("*" * i)

        # We won't get this back
        ws.send("Foobar")

    greenlets = [
        gevent.spawn(incoming),
        gevent.spawn(outgoing),
    ]
    gevent.joinall(greenlets)
