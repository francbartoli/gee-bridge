*************
How to deploy
*************

Local development
=================

Virtual environment
-------------------

.. hint:: Make sure you have entered the virtual environment where all python dependencies have been installed.

- If using `pyenv`_ facility then the command is that provided below
assuming your virtual environment is called *gee_bridge*::

.. _pyenv: https://github.com/pyenv/pyenv

    .. code-block:: bash

        pyenv activate gee_bridge

- If using `pipenv`_ facility then the command is:

.. _pipenv: https://github.com/kennethreitz/pipenv/

    .. code-block:: bash

        pipenv shell

Django server
^^^^^^^^^^^^^

As you usually do with all Django projects execute
the :command:`runserver` command:

    .. code-block:: bash

        (gee_bridge)$ python manage.py runserver

Gunicorn
^^^^^^^^

The `Gunicorn`_ HTTP WSGI server has been already declared as dependency
of your virtual environment indeed simply run:

.. _Gunicorn: http://gunicorn.org/

    .. code-block:: bash

        (gee_bridge)$ gunicorn gee_bridge.wsgi:application --config gunicorn.conf.py

where the configuration option can be a file with content
from `Gunicorn settings`_ like:

.. _Gunicorn settings: http://docs.gunicorn.org/en/latest/configure.html

.. warning:: Please make sure you **won't be** using the option `--log-file` for logging to file because GEE Bridge :ref:`Processes` Web API takes the result of **GEE** scripts from the standard output. If you enable that option the **bridge will break**!

Supervisor
^^^^^^^^^^

`Supervisor`_ can be used to control the processes of the **Gunicorn** server.
Thankfully to the `pipenv`_ ``run`` command we can work outside of the virtual
environment to start and stop our application:

**Start command**

    .. code-block:: bash

        $ pipenv run supervisord -c supervisord.conf

**Stop command**

    .. code-block:: bash

        $ ps -ef | grep supervisord # check the pid number
        $ kill -s SIGTERM $SUPERVISORD_PID_NUMBER


Cloud hosting provider
======================

Heroku
------

You can essentially follow this `guide`_:

.. _guide: https://devcenter.heroku.com/articles/deploying-python

.. warning:: It is supposed the preliminary requisites have been already performed even included the creation of a **Heroku** account and its `CLI`_  installed on you computer for working locally.

.. _CLI: https://devcenter.heroku.com/articles/heroku-cli

Ensure you are in your working virtual environment as described in :ref:`Create a virtual environment`

Follow these steps:

Declare the Python version
^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a text file named :file:`runtime.txt` with the following content:

    .. code-block:: text

        python-2.7.12

with the Python version which has to be used.

Create the Procfile to start the application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:file:`Procfile` is a text file in the root directory of your Django application where you define the process *type* and the *command* to run in such a way:

    .. code-block:: ini

        web: gunicorn gee_bridge.wsgi:application $PORT

The name :py:attr:`web` is not just a placeholder but a **key term** which declares **HTTP** traffic for the application while the environment variable :envvar:`$PORT` has been used to assign the port where to bind the process.

Alternatively you can pass a configuration option to the :command:`gunicorn` command to read address and port to bind from a file:

    .. code-block:: ini

        web: gunicorn gee_bridge.wsgi:application --config gunicorn.conf.py

Where the :file:`gunicorn.conf.py` file is something like:

    .. code-block:: python

        bind = '0.0.0.0:9000'
        workers = 3
        timeout = 30

Login to Heroku
^^^^^^^^^^^^^^^

Please let's make a logon from your current shell by executing the :command:`login` command:

    .. code-block:: bash

        heroku login

Your previously created credentials have to be provided:

    .. code-block:: text

        Enter your Heroku credentials:
        Email: mario.rossi@gmail.com
        Password: *************
        Logged in as mario.rossi@gmail.com

Create your application on Heroku
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's get started with our application by executing the :command:`apps:create` command which generates a new repository for your code with the name provided:

    .. code-block:: bash

        heroku apps:create geebridge

Heroku will provide back the url assigned to the application:

    .. code-block:: bash

        Creating ⬢ geebridge... done
        https://geebridge.herokuapp.com/

.. warning:: GEE Bridge is a Django application that strongly needs `GDAL`_, the most powerful geospatial libraries which means your environment must have such a tool already installed. **Heroku** can provide additional `buildpack`_ for this purpose. Please use the below command to create this application.

.. _buildpack: https://elements.heroku.com/buildpacks/cyberdelia/heroku-geo-buildpack
.. _GDAL: http://www.gdal.org/

    .. code-block:: bash

        heroku apps:create geebridge --buildpack https://github.com/cyberdelia/heroku-geo-buildpack.git

Start your application locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Firsty create the :file:`.env` file for defining your environment variable. In our case the *PORT* can be set by executing the :command:`config` command:

    .. code-block:: bash

       heroku config:set PORT=9000 --app geebridge  >> .env

2. Run the command below inside your root directory where you previously created the files :file:`runtime.txt` and :file:`Procfile`:

    .. code-block:: console

        heroku local web

Deploy your application to Heroku
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure you have created your application with the option to use a  which supports `GDAL`_ libraries cause our scripts are mostly relying on that.

Run the following `GIT`_ command from your *master* branch:

.. _GIT: https://git-scm.com/

.. code-block:: bash

    git push heroku master
