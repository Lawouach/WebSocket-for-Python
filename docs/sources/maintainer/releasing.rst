.. _releasing:

Release Process
===============

ws4py's release process is as follow:

1. Update the release minor or micro version. 
 
 	If necessary change also the major version. This should be saved only for major 
 	modifications and/or API compatibility breakup.
 	
	Edit ``ws4py/__init__.py`` accordingly. This will
	propagate to the ``setup.py`` and ``docs/conf.py`` appropriately on its own.
	
 	.. seealso:: `How to version? <http://semver.org/>`_ You should read this.

2. Run the unit test suites

	It's simple, fast and will make you sleep well at night. So `do it <testing>`_.
	
	If the test suite fails, do not release. It's a simple rule we constantly
	fail for some reason. So if it fails, go back and fix it.
	
3. Rebuild the documentation

	It may sound funny but a release with an out of date documentation has little
	value. Keeping your documentation up to date is as important as having
	no failing unit tests.
	
	Add to subversion any new documentation pages, both their sources and
	the resulting HTML files.
	
4. Build the source package

	First delete the ``build`` directory.

	Run the following command:
	
	.. code-block:: console
	
		python setup.py sdist --formats=gztar
	
	This will produce a tarball in the ``dist`` directory.
	
5. Push the release to PyPI

6. Tag the release in github

7. Announce it to the world :)
