************
Wapor Client
************

Wapor command
=============

.. program:: python manage.py wapor --help

Synopsis
--------

    usage: manage.py wapor [-h] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
            [--pythonpath PYTHONPATH] [--traceback] [--no-color]
            [-x, --export [{u,d,t} [{u,d,t} ...]]]
            [-i, --map_id [MAP_ID [MAP_ID ...]]]
            [-s, --arealstat ...]
            [-o, --output [{csv,json} [{csv,json} ...]]]
            [-a, --aggregation [{agbp,aet,t_frac,wp_gb,wp_nb} [{agbp,aet,t_frac,wp_gb,wp_nb} ...]]]
            [-m, --map [{agbp,aet,t_frac,wp_gb,wp_nb} [{agbp,aet,t_frac,wp_gb,wp_nb} ...]]]
            [-u, --upload [UPLOAD [UPLOAD ...]]]
            [timeframe [timeframe ...]]

    positional arguments:

    timeframe     Calculate Water Productivity Annually for the chosen period

    optional arguments:

    -h, --help            show this help message and exit
    --version             show program's version number and exit
    -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output,
                        2=verbose output, 3=very verbose output
    --settings SETTINGS   The Python path to a settings module, e.g.
                        "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be
                        used.
    --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
    --traceback           Raise on CommandError exceptions
    --no-color            Don't colorize the command output.
    -x, --export [{u,d,t} [{u,d,t} ...]]
                        Choose export to url(-u), drive (-d) or asset (-t)
    -i, --map_id [MAP_ID [MAP_ID ...]]
                        Generate map id for generating tiles
    -s, --arealstat ...   Zonal statistics form a WaterProductivity generated in
                        GEE for the chosen Country/Watershed or User Defined
                        Area
    -o, --output [{csv,json} [{csv,json} ...]]
                        Choose format fo the annual statistics csv(-o 'csv')
                        or json (-o 'json')
    -a, --aggregation [{agbp,aet,t_frac,wp_gb,wp_nb} [{agbp,aet,t_frac,wp_gb,wp_nb} ...]]
                        Aggregate dekadal data at annual level
    -m, --map [{agbp,aet,t_frac,wp_gb,wp_nb} [{agbp,aet,t_frac,wp_gb,wp_nb} ...]]
                        Show calculated output overlaid on Google Map
    -u, --upload [UPLOAD [UPLOAD ...]]
                        Upload or update data in Google Earth Engine

Options
-------

.. option:: --arealstat {g,c,w}

    Specify option for statistics.

User Defined Area example
-------------------------

    .. code-block:: bash

        python manage.py wapor 2015 -a wp_gb -i -m -s g '{"type": "FeatureCollection","crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},"features": [{"type": "Feature","properties": {"area": "user_defined"},"geometry": {"type": "Polygon","coordinates": [[[8.72, 12.28],[29.34,0.92],[20.63, -6.24],[8.72, 12.28]]]}}]}'

Country example
---------------

    .. code-block:: bash

        python manage.py wapor 2015 -a wp_gb -i -m -s c 'BEN'
