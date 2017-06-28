*************
How to deploy
*************

Local development
=================

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

:file:`Procfile` is a text file in the root directory of your Django application where you define the process *type* and the *command* to run in a such a way:

    .. code-block:: ini

        web: gunicorn gee_bridge.wsgi:application $PORT --log-file -

The name :py:attr:`web` is not just a placeholder but a **key term** which declares **HTTP** traffic for the application while the environment variable :envvar:`$PORT` has been used to assign the port where to bind the process.

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

Start your application locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Firsty create the :file:`.env` file for defining your environment variable. In our case the *PORT* can be set by executing the :command:`config` command:

    .. code-block:: env

       heroku config:set PORT=9000 --app geebridge  >> .env

2. Run the command below inside your root directory where you previously created the files :file:`runtime.txt` and :file:`Procfile`:

    .. code-block:: console

        heroku local web

