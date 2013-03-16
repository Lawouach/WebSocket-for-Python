.. _perf:

Performances
============

ws4py doesn't perform too bad but it's far from being the fastest WebSocket lib under heavy load. 
The reason is that it was first designed to implement the protocol with simplicity and clarity in mind. 
Future developments will look at performances. 

.. note::

   ws4py runs faster in some cases on PyPy than it does on CPython. 

.. note::

   The `wsaccel <https://github.com/methane/wsaccel>`_ package 
   replaces some internal bottleneck with a Cython implementation.
