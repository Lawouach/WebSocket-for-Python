# -*- coding: utf-8 -*-
__doc__ = """
This compatibility module is inspired by the one found
in CherryPy. It provides a common entry point for the various
functions and types that are used with ws4py but which
differ from Python 2.x to Python 3.x

There are likely better ways for some of them so feel
free to provide patches.

Note this has been tested against 2.7 and 3.3 only but
should hopefully work fine with other versions too.
"""
import sys

if sys.version_info >= (3, 0):
    py3k = True
    from urllib.parse import urlsplit
    range = range
    unicode = str
    basestring = (bytes, str)
    _ord = ord

    def enc(b, encoding='utf-8'):
        if isinstance(b, str):
            return b.encode(encoding)
        elif isinstance(b, bytearray):
            return bytes(b)
        return b

    def dec(b, encoding='utf-8'):
        if isinstance(b, (bytes, bytearray)):
            return b.decode(encoding)
        return b

    def get_connection(fileobj):
        return fileobj.raw._sock

    def detach_connection(fileobj):
        fileobj.detach()

    def ord(c):
        if isinstance(c, int):
            return c
        return _ord(c)
else:
    py3k = False
    from urlparse import urlsplit
    range = xrange
    unicode = unicode
    basestring = basestring
    ord = ord

    def enc(b, encoding='utf-8'):
        if isinstance(b, unicode):
            return b.encode(encoding)
        elif isinstance(b, bytearray):
            return str(b)
        return b

    def dec(b, encoding='utf-8'):
        if isinstance(b, (str, bytearray)):
            return b.decode(encoding)
        return b

    def get_connection(fileobj):
        return fileobj._sock

    def detach_connection(fileobj):
        fileobj._sock = None
