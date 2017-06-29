**************************
How to setup documentation
**************************

Build automated API from docstrings
===================================

.. note:: Docstrings are generated from a `Google`_  or `Numpy`_ style guide. This behavior can be changed by editing the `Napoleon`_ configuration within ``conf.py``:



.. code-block:: python

    # Napoleon settings
    napoleon_google_docstring = True
    napoleon_numpy_docstring = True

.. _Google: http://google.github.io/styleguide/pyguide.html#Comments

.. _Numpy: https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

.. _Napoleon: http://sphinxcontrib-napoleon.readthedocs.io/en/latest/index.html#

Run the generation of API documentation:

    make apidoc

Build the documentation
=======================

    make html

Build and serve live documentation
==================================

    make livehtml
