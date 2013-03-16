.. _testing:

Testing Overview
================

ws4py is a Python library which means it can be tested in various fashion:

- unit testing
- functional testing
- load testing

Though all of them are of useful, ws4py mostly relies on functional testing.

Unit Testing
------------

Unit testing solves complex issues in a simple fashion:

- Micro-validation of classes and functions
- Ensure non-regression after modifications
- Critique the design as early as possible for minimum impact

Too often, developers focus solely on the first two and fail
to realise how much feedback they can get by writing a simple unit tests. 
Usually starting writing unit tests can take time because your
code is too tightly coupled with itself or external dependencies. This
should not the case, most of the time anyway. 
So make sure to reflect on your code design whenever you have difficulties
setting up proper unit tests.

.. note::

  Unfortunately, for now ws4py has a rather shallow coverage as it relies
  more on the functional testing to ensure the package is sane. I hope
  to change this in the future.

Framework
^^^^^^^^^

ws4py uses the Python built-in :mod:`unittest` module. Make sure you read
its extensive documentation.

Execution
^^^^^^^^^

Test execution can be done as follow:

.. code-block:: console

	cd test
	
	python -m unittest discover  # execute all tests in the current directory
	
Tests can obviously be executed via nose, unittest2 or py.test if you prefer.

Functional Testing
------------------

ws4py relies heavily on the extensive `testing suite <http://autobahn.ws/testsuite>`_
provided by the `Autobahn <http://autobahn.ws/>`_ project.

The server test suite is used by many other WebSocket implementation out there
and provides a great way to validate interopability so it must be executed
before each release to the least. Please refer to the :ref:`requirements` 
page to install the test suite.

Execution
^^^^^^^^^

- Start the CherryPy server with PyPy 1.9

    .. code-block:: console

        pypy test/autobahn_test_servers.py --run-cherrypy-server-pypy

- Start the CherryPy server with Python 3.2 and/or 3.3 if you can. 

    .. code-block:: console

        python3 test/autobahn_test_servers.py --run-cherrypy-server-py3k

- Start all servers with Python 2.7

    .. code-block:: console

        python2 test/autobahn_test_servers.py --run-all

- Finally, execute the test suite as follow:

    .. code-block:: console

        wstest -m fuzzingclient -s test/fuzzingclient.json

The whole test suite will take a while to complete so be patient.
