# -*- coding: utf-8 -*-
"""Tests for the CherryPy and ws4py libraries with SSL support.
"""

# ruff: noqa: D102,D103,D105

import datetime
import os
import time
import unittest
from threading import Thread

import cherrypy

from ws4py.client.threadedclient import WebSocketClient
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket

root = os.path.dirname( os.path.abspath( __file__ ) )

NUMBERS_TO_SEND = 10 # send this amount of numbers back and forth between client and server
TIMEOUT_LIMIT   = 20 # CherryPy server timeout limit in seconds

global_data = {
    "sent"     : [],
    "received" : [],
    "timedout" : False,
}

class EchoClient( WebSocketClient ):
    def opened( self ):
        self.send( 1 )

    def send( self, payload, binary=False ):
        global_data[ "sent" ].append( payload )
        return super().send( str( payload ), binary )

    def closed( self, code, reason=None ):
        cherrypy.engine.exit()  # close the CherryPy server

    def received_message( self, m ):
        m = str( m ).strip()
        try:
            number = int( m )
            global_data[ "received" ].append( number )
            if number < NUMBERS_TO_SEND:
                # increase number and send it back
                self.send( number + 1 )
            else:
                self.close( 1000, "Done" )
        except ( TypeError, ValueError ):
            return


class BroadcastWebSocketHandler( WebSocket ):
    def received_message( self, message ):
        cherrypy.engine.publish( 'websocket-broadcast', str( message ) )


class Root:
    @cherrypy.expose
    def ws( self ):
        pass


def wait_for_cherrypy_engine_started():
    while ( cherrypy.engine.state != cherrypy.engine.states.STARTED ):
        time.sleep( 0.5 )


def run_echo_client( url ):
    wait_for_cherrypy_engine_started()
    try:
        ws = EchoClient( url )
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()


def run_echo_client_thread( host, port, ssl = False ):
    """Run the EchoClient in a separate thread.
    """
    url = "wss://%s:%d/ws" % (host, port) if ssl else "ws://%s:%d/ws" % (host, port)
    t   = Thread( target=run_echo_client, daemon=True, name="WebSocketClient", args=( url, ) )
    t.start()
    return t


def run_cherrypy_server( host, port, ssl = False ):
    config = {
        "global" : {
            "server.ssl_module"      : "builtin" if ssl else None,
            "server.ssl_certificate" : os.path.join( root, "server.crt" ) if ssl else None,
            "server.ssl_private_key" : os.path.join( root, "server.key" ) if ssl else None,
            "server.socket_host"     : host,
            "server.socket_port"     : port,
            "log.screen"             : False,
            'engine.autoreload.on'   : False,
        },
        "/ws" : {
            "tools.websocket.on"          : True,
            "tools.websocket.handler_cls" : BroadcastWebSocketHandler,
            'tools.websocket.protocols'   : [ 'some-protocol' ],
            'tools.gzip.on'               : False,
            'tools.caching.on'            : False,
            'tools.sessions.on'           : False,
        },
    }

    WebSocketPlugin( cherrypy.engine ).subscribe()
    cherrypy.tools.websocket = WebSocketTool()
    cherrypy.quickstart( Root(), "/", config=config )


class TimeoutSignaller( Thread ):
    def __init__( self, limit, handler ):
        Thread.__init__( self, name="TimeoutSignaller" )
        self.limit   = limit
        self.running = True
        self.handler = handler
        self.daemon  = True
        assert callable( handler ), "Timeout Handler needs to be a method"

    def run( self ):
        timeout_limit = datetime.datetime.now() + datetime.timedelta( seconds=self.limit )
        while self.running:
            if datetime.datetime.now() >= timeout_limit:
                self.handler()
                self.stop_run()
                break

    def stop_run( self ):
        self.running = False


class CherryPyTimeout:
    def __init__( self, seconds=0, minutes=0, hours=0 ):
        self.seconds = ( hours * 3600 ) + ( minutes * 60 ) + seconds
        self.signal  = TimeoutSignaller( self.seconds, self.signal_handler )
        self.ok      = True

    def __enter__( self ):
        self.signal.start()
        return self

    def __exit__( self, exc_type, exc_val, exc_tb ):
        self.signal.stop_run()

    def done( self ):
        self.signal.stop_run()

    def signal_handler( self ):
        if cherrypy.engine.state == cherrypy.engine.states.STARTED:
            global_data[ "timedout" ] = True
            cherrypy.engine.exit()
            self.ok = False


def run( host, port, ssl ):
    run_echo_client_thread( host, port, ssl=ssl )
    run_cherrypy_server( host=host, port=port, ssl=ssl )


def run_with_timeout( host, port, ssl ):
    with CherryPyTimeout( seconds=TIMEOUT_LIMIT ) as t:
        run( host=host, port=port, ssl=ssl )
        t.done()
        if not t.ok:
            global_data[ "timedout" ] = True
            raise TimeoutError( "CherryPy server timed out" )

class CherryPySSLTest(unittest.TestCase):
    def test_ssl( self ):
        global_data[ "sent" ]     = []
        global_data[ "received" ] = []
        global_data[ "timedout" ] = False

        run_with_timeout( host="127.0.0.1", port=8877, ssl=True )

        assert not global_data[ "timedout" ], "Test timed out"
        assert len( global_data[ "sent" ] ) > 0, "No data sent to the server"
        assert len( global_data[ "received" ] ) > 0, "No data received from the server"
        assert global_data[ "sent" ] == global_data[ "received" ], "Sent and received data do not match"
        assert global_data[ "sent" ] == list( range( 1, NUMBERS_TO_SEND + 1 ) ), "Sent data does not match expected data"


if __name__ == "__main__":
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [CherryPySSLTest]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
