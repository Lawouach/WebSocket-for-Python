.. _documenting:

Documentation process
=====================

Basic principles
----------------

Document in that order: why, what, how
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Documenting ws4py is an important process since the code doesn't always carry enough
information to understand its design and context. Thus, documenting should target the
question "why?" first then the "what?" and "how?". It's actually trickier than it sound.

Explicit is better than implicit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you have your nose in the code it may sound straightforward enough not to document
certain aspects of pyalm. Remember that :pep:`20` principle:
**Explicit is better than implicit**.

Be clear, not verbose
^^^^^^^^^^^^^^^^^^^^^

Finding the right balance between too much and not enough is hard. Writing
good documentation is just difficult. However, you should not be too verbose either.

Add enough details to a section to provide context but don't flood the reader
with irrelevant information.

Show me where you come from
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every piece of code should be contextualized and almost every time you should
explicitely indicate the import statement so that the reader doesn't wonder
where an object comes from.

Consistency for the greater good
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A user of ws4py should feel at ease with any part of the library and shouldn't
have to switch to a completely new mental model when going through
the library or documentation. Please refer again to :pep:`8`.

Documentation Toolkit
---------------------

pyalm uses the Sphinx documentation generator toolkit so refer to its 
`documentation <http://sphinx-doc.org/contents.html>`_ to learn more on its usage.

Building the documentation is as simple as:

	.. code-block:: console
	
		cd docs
		make html
		
The generated documentation will be available in ``docs\_build\html``.
	
