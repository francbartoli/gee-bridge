********
REST API
********

Rasterbucket API overview
=========================

The API is accessible on the ``/api/`` URL and it is based on
`Django REST framework <http://www.django-rest-framework.org/>`_.
You can use it directly or by :ref:`geebridge`. @TODO

GEE Bridge APIs can be discovered in different format at this endpoint
``http://localhost:9000/api/v1/swagger/?format=openapi`` which exposes an
`OpenAPI`_ specification using the query string parameter :literal:`format=openapi`:

.. _OpenAPI: https://www.openapis.org/

Possible options for the value of `format` are:

    - :literal:`format=swagger` - `Swagger`_ specification format
    - :literal:`format=api`     - `Django Rest Framework`_ specification format
    - :literal:`format=json`    - `JSON`_ specification format

    .. _Swagger: https://swagger.io
    .. _Django Rest Framework: http://www.django-rest-framework.org/
    .. _JSON: http://www.json.org/

A list of endpoints and their specification can be found below after running
the server from a live instance:

.. swaggerv2doc:: http://localhost:9000/api/v1/swagger/?format=openapi

Rasterbucket
------------

RasterbucketServices
--------------------

Processes
---------

# TODO
# https://github.com/WeblateOrg/weblate/blob/master/docs/api.rst
Process List
````````````

.. http:get:: /api/v1/processes/

    Returns a list of all processes.

    .. seealso::

        Additional common headers, parameters and status codes are documented
        at :ref:`api-generic`.

        Process object attributes are documented
        at :http:get:`/api/v1/processes/`.

Example Usage
^^^^^^^^^^^^^
Request:

    .. code-block:: http

        GET /api/v1/processes/ HTTP/1.1
        Host: example.org
        Authorization: Token 46806a08bf54136e9597e879ed3a0876113fdee6

Response:

    .. code-block:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {}

Process Detail
``````````````

.. http:get:: /api/v1/processes/(string:id)/

    Returns information about a process.

    :param id: Process code
    :type id: string
    :>json string id: Process code
    :>json string name: Process name
    :>json object input_data: Input data object for the process
    :>json string process: Process type name
    :>json array arguments: Process arguments for gee script

    .. seealso::

        Additional common headers, parameters and status codes are documented
        at :ref:`api-generic`.

Example Usage
^^^^^^^^^^^^^
Request:

    .. code-block:: http

        GET /api/v1/processes/(string:id) HTTP/1.1
        Host: example.org
        Authorization: Token 46806a08bf54136e9597e879ed3a0876113fdee6

Response:

    .. code-block:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
            "id": "00a2ce69-2284-4d20-af18-f7afffa54f48",
            "name": "A wapor productivity process",
            "input_data": {
                "process": "wapor",
                "arguments": [
                    {
                        "positional": true,
                        "timeframe": [
                            {
                                "startdate": "2015-1-1",
                                "enddate": "2015-12-31"
                            }
                        ]
                    },
                    {
                        "positional": false,
                        "map_id": true
                    },
                    {
                        "positional": false,
                        "aggregation": "wp_gb"
                    },
                    {
                        "positional": false,
                        "arealstat": {
                            "option": "g",
                            "choices": {
                                "type": "FeatureCollection",
                                "features": [
                                    {
                                        "geometry": {
                                            "type": "Polygon",
                                            "coordinates": [
                                                [
                                                    [
                                                        17.578125,
                                                        19.31114335506464
                                                    ],
                                                    [
                                                        32.6953125,
                                                        -3.513421045640032
                                                    ],
                                                    [
                                                        34.453125,
                                                        19.31114335506464
                                                    ],
                                                    [
                                                        17.578125,
                                                        19.31114335506464
                                                    ]
                                                ]
                                            ]
                                        },
                                        "type": "Feature",
                                        "properties": {}
                                    }
                                ]
                            }
                        },
                        "choice": true
                    }
                ]
            },
            "owner": "wapor",
            "output_data": {
                "gee_stats": {
                    "response": {
                        "stats": {
                            "max": 2.2239012915851273,
                            "sum": 192173.8123681499,
                            "min": 0,
                            "mean": 0.03866244260812292
                        },
                        "name": {
                            "type": "FeatureCollection",
                            "features": [
                                {
                                    "geometry": {
                                        "type": "Polygon",
                                        "coordinates": [
                                            [
                                                [
                                                    17.578125,
                                                    19.31114335506464
                                                ],
                                                [
                                                    32.6953125,
                                                    -3.513421045640032
                                                ],
                                                [
                                                    34.453125,
                                                    19.31114335506464
                                                ],
                                                [
                                                    17.578125,
                                                    19.31114335506464
                                                ]
                                            ]
                                        ]
                                    },
                                    "type": "Feature",
                                    "properties": {}
                                }
                            ]
                        }
                    }
                },
                "gee_maps": {
                    "eta": {
                        "token": "dc396fb39cde02f1dbccc4b17c6760be",
                        "mapid": "0b0492f66da3cc271e235d823a3ff34f",
                        "image": {
                            "bands": [
                                {
                                    "crs": "EPSG:4326",
                                    "crs_transform": [
                                        1,
                                        0,
                                        0,
                                        0,
                                        1,
                                        0
                                    ],
                                    "id": "b1",
                                    "data_type": {
                                        "type": "PixelType",
                                        "precision": "double"
                                    }
                                }
                            ],
                            "type": "Image"
                        }
                    },
                    "wp_gross": {
                        "token": "4a531ab7eba4ba9a1926de286d661fb7",
                        "mapid": "183bd47815a951fa3d07d1394c4b85d5",
                        "image": {
                            "bands": [
                                {
                                    "crs": "EPSG:4326",
                                    "crs_transform": [
                                        1,
                                        0,
                                        0,
                                        0,
                                        1,
                                        0
                                    ],
                                    "id": "b1",
                                    "data_type": {
                                        "type": "PixelType",
                                        "precision": "double"
                                    }
                                },
                                {
                                    "crs": "EPSG:4326",
                                    "crs_transform": [
                                        1,
                                        0,
                                        0,
                                        0,
                                        1,
                                        0
                                    ],
                                    "id": "days_in_dk",
                                    "data_type": {
                                        "type": "PixelType",
                                        "precision": "double"
                                    }
                                }
                            ],
                            "type": "Image"
                        }
                    },
                    "agbp": {
                        "token": "09a10d9d219f7708457299078d27b4d1",
                        "mapid": "abcd9b58fef989599665e9f736da6f68",
                        "image": {
                            "bands": [
                                {
                                    "crs": "EPSG:4326",
                                    "crs_transform": [
                                        1,
                                        0,
                                        0,
                                        0,
                                        1,
                                        0
                                    ],
                                    "id": "b1",
                                    "data_type": {
                                        "type": "PixelType",
                                        "precision": "double"
                                    }
                                },
                                {
                                    "crs": "EPSG:4326",
                                    "crs_transform": [
                                        1,
                                        0,
                                        0,
                                        0,
                                        1,
                                        0
                                    ],
                                    "id": "days_in_dk",
                                    "data_type": {
                                        "type": "PixelType",
                                        "precision": "double"
                                    }
                                }
                            ],
                            "type": "Image"
                        }
                    }
                },
                "gee_errors": []
            },
            "date_created": "2017-11-08T15:04:08.014776Z",
            "date_modified": "2017-11-08T15:04:08.014828Z"
        }

.. http:post:: /api/v1/processes/

    Performs the given process type on Google Earth Engine.

    See :http:post:`/api/v1/processes/` for documentation.

    :<json string option: Option for the operation to perform, one of ``g``, ``c`` or ``w`` which mean ``User Defined Area``, ``Country`` or ``Watershed``
    :<json string/object choices: Choices can be a plain string with a country ``iso3`` code or a ``GeoJSON`` object
    :<json object output_data: result of the operation. Initially empty

    .. seealso::

        Additional common headers, parameters and status codes are documented at :ref:`api-generic`.

    **User Defined Area (UDA) example JSON data:**

    .. code-block:: json

        {
            "name": "A wapor productivity process",
            "input_data": {
                "process": "wapor",
                "arguments": [
                    {
                        "positional": true,
                        "timeframe": [
                            {
                                "startdate": "2015-1-1",
                                "enddate": "2015-12-31"
                            }
                        ]
                    },
                    {
                        "positional": false,
                        "map_id": true
                    },
                    {
                        "positional": false,
                        "aggregation": "wp_gb"
                    },
                    {
                        "positional": false,
                        "arealstat": {
                            "option": "g",
                            "choices": {
                                "type": "FeatureCollection",
                                "features": [
                                    {
                                        "geometry": {
                                            "type": "Polygon",
                                            "coordinates": [
                                                [
                                                    [
                                                        17.578125,
                                                        19.31114335506464
                                                    ],
                                                    [
                                                        32.6953125,
                                                        -3.513421045640032
                                                    ],
                                                    [
                                                        34.453125,
                                                        19.31114335506464
                                                    ],
                                                    [
                                                        17.578125,
                                                        19.31114335506464
                                                    ]
                                                ]
                                            ]
                                        },
                                        "type": "Feature",
                                        "properties": {}
                                    }
                                ]
                            }
                        },
                        "choice": true
                    }
                ]
            },
            "owner": "wapor",
            "output_data": {}
        }

    **Country example JSON data:**

    .. code-block:: json

        {
            "name": "A wapor productivity process",
            "input_data": {
                "process": "wapor",
                "arguments": [
                    {
                        "positional": true,
                        "timeframe": [
                            {
                                "startdate": "2015-1-1",
                                "enddate": "2015-12-31"
                            }
                        ]
                    },
                    {
                        "positional": false,
                        "map_id": true
                    },
                    {
                        "positional": false,
                        "aggregation": "wp_gb"
                    },
                    {
                        "positional": false,
                        "arealstat": {
                            "option": "c",
                            "choices": "BEN"
                        },
                        "choice": true
                    }
                ]
            },
            "owner": "wapor",
            "output_data": {}
        }
