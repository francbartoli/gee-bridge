**************************
How to setup documentation
**************************

Save a JSON representation of the swagger schema
================================================

Install a command utility for fetching resource from the web. `curl` and `wget` are fine but if you like pythonic tool then `httpie`_ is a greater one. You can install that and then run the following command from the terminal:

    http http://localhost:9000/api/v1/swagger\?format\=openapi --download --output swagger/schema.json

.. _httpie: https://httpie.org/

Generate API documentation with Redoc extension
===============================================

Create a script to overcome the lack of a swagger schema in `yaml` format from `django-restframework-swagger` package.

.. code-block:: python

    #!/usr/bin/env python

    from pyswagger import App
    import yaml


    app = App.create('http://localhost:9000/api/v1/swagger?format=openapi')
    obj = app.dump()
    with open('./swagger/schema.yaml', 'w') as w:
         w.write(yaml.safe_dump(obj))

Save the content above in a file :file:`openapi2redoc.py` under the directory `docs` then run it and generate the `yaml` formatted schema for swagger specification:

    python openapi2redoc.py

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

If you want to browse live documentation for the API with the `ReDoc`_ template then you can open the following `link`_

.. _link: http://localhost:8000/api/rasterbuckets/index.html

.. _ReDoc: https://rebilly.github.io/ReDoc/
