Server
======

CherryPy
--------

ws4py provides an extension to CherryPy 3 to enable WebSocket from the framework layer. It is based on the CherryPy `plugin <http://docs.cherrypy.org/stable/concepts/engine.html>`_ and `tool <http://docs.cherrypy.org/stable/concepts/tools.html>`_ mechanisms.

The :class:`WebSocket tool <ws4py.server.cherrypyserver.WebSocketTool>` plays at the request level on every request received by the server. Its goal is to perform the WebSocket handshake and, if it succeeds, to create the :class:`WebSocket <ws4py.websocket.WebSocket>` instance (well a subclass you will be implementing) and push it to the plugin.

The :class:`WebSocket plugin <ws4py.server.cherrypyserver.WebSocketPlugin>` works at the CherryPy system level and has a single instance throughout. Its goal is to track websocket instances created by the tool and free their resources when connections are closed.

Here is a simple example of an echo server:

.. code-block:: python
    :linenos:

    import cherrypy
    from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
    from ws4py.websocket import EchoWebSocket
    
    cherrypy.config.update({'server.socket_port': 9000})
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    class Root(object):
        @cherrypy.expose
        def index(self):
            return 'some HTML with a websocket javascript connection'

        @cherrypy.expose
        def ws(self):
            # you can access the class instance through
	    handler = cherrypy.request.ws_handler
        
    cherrypy.quickstart(Root(), '/', config={'/ws': {'tools.websocket.on': True,
                                                     'tools.websocket.handler_cls': EchoWebSocket}})


Note how we specify the class which should be instanciated by the server on each connection. The great aspect of the tool mechanism is that you can specify a different class on a per-path basis.


gevent
------

`gevent <http://www.gevent.org/>`_ is a coroutine, called greenlets, implementation for very concurrent applications. ws4py offers a server implementation for this library on top of the `WSGI protocol <http://www.wsgi.org/en/latest/index.html>`_. Using it is as simple as:

.. code-block:: python
    :linenos:

    from gevent import monkey; monkey.patch_all()
    from ws4py.websocket import EchoWebSocket
    from ws4py.server.geventserver import WSGIServer
    from ws4py.server.wsgiutils import WebSocketWSGIApplication

    server = WSGIServer(('localhost', 9000), WebSocketWSGIApplication(handler_cls=EchoWebSocket))
    server.serve_forever()

First we patch all the standard modules so that the stdlib runs well with as gevent. Then we simply create a `WSGI <http://www.wsgi.org/en/latest/index.html>`_ server and specify the class which will be instanciated internally each time a connection is successful.

wsgiref
-------

:py:mod:`wsgiref` is a built-in WSGI package that provides various classes and helpers to develop against WSGI. Mostly it provides a basic WSGI server that can be usedfor testing or simple demos. ws4py provides support for websocket on wsgiref for testing purpose as well. It's not meant to be used in production.

.. code-block:: python
    :linenos:



    from wsgiref.simple_server import make_server
    from ws4py.websocket import EchoWebSocket
    from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
    from ws4py.server.wsgiutils import WebSocketWSGIApplication

    server = make_server('', 9000, server_class=WSGIServer,
                         handler_class=WebSocketWSGIRequestHandler,
                         app=WebSocketWSGIApplication(handler_cls=EchoWebSocket))
    server.initialize_websockets_manager()
    server.serve_forever()
