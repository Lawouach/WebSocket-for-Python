Install ws4py
=============

Get the code
------------

ws4py is hosted on `github <https://github.com/Lawouach/WebSocket-for-Python>`_ and can be retrieved from there:

.. code-block:: console
    
    $ git clone git@github.com:Lawouach/WebSocket-for-Python.git


Installing the ws4py package is performed as usual:

.. code-block:: console
    
    $ python setup.py install

However, since ws4py is referenced in `PyPI <http://pypi.python.org/pypi/ws4py>`_, it can also be installed through easy_install, distribute or pip:

.. code-block:: console
    
    $ pip install ws4py
    $ easy_install ws4py
   
.. note::

   ws4py explicitely will not automatically pull out its dependencies. Please install them
   manually depending on which imlementation you'll be using.
