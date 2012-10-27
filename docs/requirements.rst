Python
======

ws4py requires Python 2.7+ or Python 3+.
It also works with PyPy 1.8+.
Note that ws4py will not try to automatically install dependencies and will
let you decide which one you need.

Client
======

ws4py comes with three client implementation depending of your own needs.

**Built-in**

That client is solely based on the Python stdlib, it uses a thread to run the inner processing loop.

**Tornado**

The Tornado client requires Tornado 2.0+

**gevent**

The gevent client requires gevent 0.13.6 or 1.0.0-dev

Server
======

ws4py comes with two server implementation depending of your own needs.

**CherryPy**

The CherryPy server requires CherryPy 3.2.2+

**gevent**

The gevent server requires gevent 0.13.6 or 1.0.0-dev
