****************
Rasterbucket API
****************

Models design
=============

UML diagram
-----------

.. image:: _images/uml/api_models.png

API overview
============

GEE Bridge APIs can be discovered in different format at this endpoint ``http://localhost:9000/api/v1/swagger/?format=openapi`` which exposes an `OpenAPI`_ specification using the query string parameter :literal:`format=openapi`:

.. _OpenAPI: https://www.openapis.org/

Possible options for the value of `format` are:

    - :literal:`format=swagger` - `Swagger`_ specification format
    - :literal:`format=api`     - `Django Rest Framework`_ specification format
    - :literal:`format=json`    - `JSON`_ specification format

    .. _Swagger: https://swagger.io
    .. _Django Rest Framework: http://www.django-rest-framework.org/
    .. _JSON: http://www.json.org/

A list of endpoints and their specification can be found below after running the server from a live instance:

.. swaggerv2doc:: http://localhost:9000/api/v1/swagger/?format=openapi

Rasterbucket
------------

RasterbucketServices
--------------------

Processes
---------


