**************************
Google Earth Engine Bridge
**************************

Rasterbuckets
=============
TODO

API
===
TODO

How to run
==========

Using Gunicorn
--------------

.. code-block:: console

    (env)$ gunicorn gee_bridge.wsgi:application --bind 0.0.0.0:8000

Handle static assets
^^^^^^^^^^^^^^^^^^^^

Suppose your settings are configured as below:

.. code-block:: python

    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.9/howto/static-files/
    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
    STATIC_URL = '/static/'

    # Extra places for collectstatic to find static files.
    STATICFILES_DIRS = (
        os.path.join(PROJECT_ROOT, 'static'),
    )

Integrate Whitenoise
""""""""""""""""""""

Install the package:

.. code-block:: console

    (env)$ pip install whitenoise
    (env)$ pip freeze > requirements.txt

Embed this library in your application by editing the `wsgi.py` file:


.. code-block:: python

    from django.core.wsgi import get_wsgi_application
    from whitenoise.django import DjangoWhiteNoise

    application = get_wsgi_application()
    application = DjangoWhiteNoise(application)

Using Supervisord
-----------------

Create a configuration file:

.. code-block:: console

    (env)$ echo_supervisord_conf > supervisord.conf

.. code-block:: console

    (env)$ supervisord -c supervisord.conf
