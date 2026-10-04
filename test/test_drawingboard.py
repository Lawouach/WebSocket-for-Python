import os
import sys
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import cherrypy
from cherrypy.process.wspbus import Bus


example_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                           'example', 'websensors')
sys.path.insert(0, example_dir)
try:
    with patch.object(cherrypy.tools, 'render', create=True), \
            patch.object(cherrypy.tools, 'websocket', create=True):
        import app as drawingboard
finally:
    sys.path.remove(example_dir)


class DrawingBoardTest(unittest.TestCase):
    def setUp(self):
        self.bus = Bus()
        self.plugin = drawingboard.DrawingBoardWebSocketPlugin(self.bus)
        self.bus.websockets = self.plugin
        self.plugin.register_board('board')
        self.alice = drawingboard.DrawingBoardWebSocketHandler(None)
        self.bob = drawingboard.DrawingBoardWebSocketHandler(None)
        self.plugin.register_participant('board', 'alice', self.alice)
        self.plugin.register_participant('board', 'bob', self.bob)

    def test_unregister_participant_preserves_other_handlers(self):
        self.plugin.unregister_participant('board', 'alice')
        self.assertEqual(self.plugin.boards['board']['handlers'],
                         {'bob': self.bob})

    def test_closed_callback_unregisters_participant(self):
        with patch.object(drawingboard, 'bus', self.bus):
            self.alice.closed(1000, 'done')
        self.assertEqual(self.plugin.boards['board']['handlers'],
                         {'bob': self.bob})

    def test_unknown_and_repeated_unregistration_are_harmless(self):
        self.plugin.unregister_participant('board', 'alice')
        self.plugin.unregister_participant('board', 'alice')
        self.plugin.unregister_participant('board', 'unknown')
        self.plugin.unregister_participant('unknown', 'bob')
        self.assertEqual(self.plugin.boards['board']['handlers'],
                         {'bob': self.bob})
