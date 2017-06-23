**************************
How to setup documentation
**************************

Build automated API from docstrings
===================================

.. note:: Docstrings are generated from a Google or Numpy style guide. This behavior can be changed by editing the Napoleon configuration within conf.py:

    # Napoleon settings
    napoleon_google_docstring = True
    napoleon_numpy_docstring = True

Run the generation of API documentation:

    make apidoc

Build the documentation
=======================

    make html

Build and serve live documentation
==================================

    make livehtml
