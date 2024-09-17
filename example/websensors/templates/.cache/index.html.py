# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1396804510.682649
_enable_loop = True
_template_filename = '/home/sylvain/Dev/projects/WebSocket-for-Python/example/websensors/templates/index.html'
_template_uri = 'index.html'
_source_encoding = 'utf-8'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        boardid = context.get('boardid', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<!DOCTYPE html>\n<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->\n<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->\n<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->\n<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->\n    <head>\n        <meta charset="utf-8">\n        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">\n        <title>Shared drawing board</title>\n        <meta name="description" content="Remote control your webapp with your mobile device">\n        <meta name="viewport" content="width=device-width, initial-scale=1">\n        <meta name="twitter:card" content="Sylvain Hellegouarch\'s twitter account">\n        <meta name="twitter:site" content="@lawouach">\n        <meta name="twitter:url" content="http://www.defuze.org">\n\n        <link rel="stylesheet" href="/static/vendors/initializr/css/normalize.min.css">\n        <link rel="stylesheet" href="/static/vendors/initializr/css/main.css">\n\n        <script src="/static/vendors/initializr/js/vendor/modernizr-2.6.2-respond-1.1.0.min.js"></script>\n    </head>\n    <body>\n        <!--[if lt IE 7]>\n            <p class="browsehappy">You are using an <strong>outdated</strong> browser. Please <a href="http://browsehappy.com/">upgrade your browser</a> to improve your experience.</p>\n        <![endif]-->\n\n        <div class="header-container">\n            <header class="wrapper clearfix">\n                <h1 class="title">shared drawing board</h1>\n            </header>\n        </div>\n\n        <div class="main-container">\n            <div class="main wrapper clearfix">\n\n                <article>\n                    <section>\n\t                <p>This demo will demonstrate a fun usage of WebSocket and Canvases.\n\t                   The idea is that you will share a drawing board with other\n\t                   users or devices and each time someone will draw something onto\n\t                   the canvas, all other participants will see the drawing in near real-time\n\t                   on their side too.\n\t                </p>\n\t                <p>Please use the link below to share a drawing board:</p>\n\t                <p><a href="http://192.168.1.13:8080/board/')
        # SOURCE LINE 44
        __M_writer(str(boardid))
        __M_writer(u'">http://192.168.1.13:8080/board/')
        __M_writer(str(boardid))
        __M_writer(u'</a></p>\n                    </section>\n                </article>\n\n            </div> <!-- #main -->\n        </div> <!-- #main-container -->\n\n        <div class="footer-container">\n            <footer class="wrapper">\n                <p>&copy; 2014 | <a href="http://www.defuze.org/">Sylvain Hellegouarch</a></p>\n            </footer>\n        </div>\n\n        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>\n        <script type="application/javascript" src="/static/vendors/initializr/js/plugins.js"></script>\n    </body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


