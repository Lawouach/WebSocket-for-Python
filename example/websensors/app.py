# -*- coding: utf-8 -*-
"""
WebSocket demo with a twist.

The idea of this little demo is to demonstrate
how it can enable interesting functions when coupled with
other HTML5 features, such as Canvas.

In this scenario, we create a canvas that we call a drawing
board. You can draw circles with various colors. A board
has a unique URL, every client connecting to that URL
can see whatever is drawn by other participants. All events
from one client are sent to other clients through
websockets. All other clients then draw on their view
events they receive.

This ought to work well with any HTML5 capable browser such
as Chrome, Firefox, Opera. It even works well on Android using
Chrome. Internet Explorer users... well it may work as well.

This demo uses:

* CherryPy 3.2.5+
* Mako
* jcanvas
* jquery
* HTML5boilerplate (via http://www.initializr.com/)

Once you have installed those dependencies, simply run the
application as follow:

  $ python app.py --baseurl https://myhost/ --host 0.0.0.0 --port 8080

You can specify the base url which will be used to build the
URL to the board. For instance, a board's url will be:

 https://myhost/board/c866

"""
import json
import os.path
import tempfile
import time
import uuid

try:
    import wsaccel
    wsaccel.patch_ws4py()
except ImportError:
    pass

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket

import cherrypy
from cherrypy.process import plugins
from mako.lookup import TemplateLookup
from mako.template import Template

BASE_URL = None

cwd_dir = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
bus = cherrypy.engine
lookup = TemplateLookup(directories=os.path.join(cwd_dir, 'templates'),
                        module_directory=os.path.join(cwd_dir, 'templates', '.cache'),
                        input_encoding='utf-8',
                        output_encoding='utf-8',
                        collection_size=20)

class DrawingBoardWebSocketHandler(WebSocket):
    """
    WebSocket handler that will dispatch drawing events
    from this client to all other registered clients
    on this board.

    An instance of this class is automatically created
    when a client is connected. The `board_id` and
    `participant_id` attributes are set outside of this
    class, when the client is registered to the board.
    """
    
    def closed(self, code, reason):
        """
        Called whenever the websocket connection is terminated,
        whether abruptly or normally.
        """
        bus.websockets.unregister_participant(self.board_id,
                                              self.participant_id)
        
    def received_message(self, m):
        """
        Received messages contain events from the
        user interface, like coordinates. They are
        dispatched to all registered participants on this
        board.
        """
        bus.websockets.broadcast_state(self.board_id,
                                       self.participant_id,
                                       m)

class DrawingBoardWebSocketPlugin(WebSocketPlugin):
    def __init__(self, bus):
        """
        This plugin is the board controller. It keeps
        track of all boards and their registered participants.

        You may access the global instance of this plugin
        through the `bus.websockets` attribute.
        """
        WebSocketPlugin.__init__(self, bus)

        # every 30s, we check if we have dead boards
        # and we clean them
        plugins.Monitor(bus, self.drop_dead_boards, 30).subscribe()
    
        # board index to quickly retrieve
        # clients of a given board
        self.boards = {}

    def drop_dead_boards(self):
        """
        Iterate over all boards and unregister any
        that seem to be unused anymore (because it doesn't
        have any connected client anymore), or that
        have been created for too long (no more than than 5mn
        are allowed).
        """
        for board_id in self.boards.copy():
            board = self.boards[board_id]
            if not board['handlers']:
                self.unregister_board(board_id)
            elif (time.time() - board['created']) > 300:
                for ws in board['handlers'].itervalues():
                    if not ws.terminated:
                        ws.close(1001, "Board can't exist for more than 5mn")
                self.unregister_board(board_id)
        
    def register_board(self, board_id):
        """
        Register a board and initialize it
        so that it'll accept participants.
        """
        if board_id not in self.boards:
            self.bus.log("Registering board %s" % board_id)
            self.boards[board_id] = {'handlers': {}, 'created': time.time()}
            
    def unregister_board(self, board_id):
        """
        Unregister a board and make it unusable.
        """
        self.boards.pop(board_id, None)

    def register_participant(self, board_id, participant_id, ws_handler):
        """
        Register a participant to the given board.
        We also set the `board_id` and `participant_id`
        attributes on the websocket handler instance.
        """
        if board_id in self.boards:
            self.bus.log("Registering participant %s to board %s" % (participant_id, board_id))
            ws_handler.board_id = board_id
            ws_handler.participant_id = participant_id
            self.boards[board_id]['handlers'][participant_id] = ws_handler
        
    def unregister_participant(self, board_id, participant_id):
        """
        Unregister a participant from this board.

        Usually this is called automatically when the client
        has closed its connection.
        """
        if board_id in self.boards:
            board = self.boards[board_id]
            if participant_id in self.boards[board_id]:
                board['handlers'].pop(participant_id, None)
                self.bus.log("Unregistering participant %s from board %s" % (participant_id, board_id))

    def broadcast_state(self, board_id, from_participant_id, state):
        """
        Dispatch the given `state` to all registered participants
        of the board (except the sender itself of course).
        """
        if board_id not in self.boards:
            return

        board = self.boards[board_id]
        
        for (participant_id, ws) in board['handlers'].iteritems():
            if from_participant_id != participant_id:
                if not ws.terminated:
                    ws.send(state)


def render_template(template):
    """
    Renders a mako template to HTML and
    sets the CherryPy response's body with it.
    """
    if cherrypy.response.status > 399:
        return

    data = cherrypy.response.body or {}
    template = lookup.get_template(template)

    if template and isinstance(data, dict):
        cherrypy.response.body = template.render(**data)

# Creating our tool so that they can be
# used below in the CherryPy applications
cherrypy.tools.render = cherrypy.Tool('before_finalize', render_template)
cherrypy.tools.websocket = WebSocketTool()

        
# Web Application
class SharedDrawingBoardApp(object):
    @cherrypy.expose
    @cherrypy.tools.render(template='index.html')
    def index(self):
        return {'boardid': str(uuid.uuid4())[:4],
                'baseurl': BASE_URL}

    @cherrypy.expose
    @cherrypy.tools.render(template='board.html')
    def board(self, board_id):
        bus.websockets.register_board(board_id)
        return {'boardid': board_id.replace('"', ''),
                'participantid': str(uuid.uuid4())[:6],
                'baseurl': BASE_URL,
                'basewsurl': BASE_URL.replace('http', 'ws')}

# WebSocket endpoint
class SharedDrawingBoarWebSocketApp(object):
    @cherrypy.expose
    @cherrypy.tools.websocket(handler_cls=DrawingBoardWebSocketHandler)
    def index(self, board_id, participant_id):
        bus.websockets.register_participant(board_id, participant_id,
                                            cherrypy.request.ws_handler)
        
if __name__ == '__main__':
    import argparse
    from urlparse import urlparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--baseurl', default='http://0.0.0.0:8080')
    parser.add_argument('--host')
    parser.add_argument('-p', '--port', type=int)
    parser.add_argument('--verbose', action="store_true")
    args = parser.parse_args()

    BASE_URL = args.baseurl
    BASE_URL = BASE_URL.rstrip('/')
    url = urlparse(BASE_URL)
    
    bus.websockets = DrawingBoardWebSocketPlugin(bus)
    bus.websockets.subscribe()

    cherrypy.config.update({
        'server.socket_host': args.host or url.hostname,
        'server.socket_port': args.port or url.port,
        'server.thread_pool': 30,
        'log.screen': args.verbose,
        'log.access_file': os.path.join(cwd_dir, 'access.log'),
        'log.error_file': os.path.join(cwd_dir, 'error.log'),
        'tools.staticfile.root': cwd_dir,
        'tools.staticdir.root': cwd_dir,
        'tools.proxy.on': True,
        'tools.proxy.base': '%s://%s' % (url.scheme, url.netloc),
        'error_page.404': os.path.join(cwd_dir, "templates", "404.html")
    })

    app = SharedDrawingBoardApp()
    app.ws = SharedDrawingBoarWebSocketApp()
    
    cherrypy.tree.mount(app, '/', {
        '/': {
            'tools.encode.on': False,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [
                ('X-Frame-options', 'deny'),
                ('X-XSS-Protection', '1; mode=block'),
                ('X-Content-Type-Options', 'nosniff')
            ]
        },
        '/robots.txt': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': 'static/robots.txt'
        },
        '/static/demos/drawing': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static'
        }
    })

    bus.signals.subscribe()
    bus.start()
    bus.block()
    
    
    
    
