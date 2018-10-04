#!/bin/bash

# make database migrations
python manage.py makemigrations --noinput --settings=gee_bridge.settings

# apply database migrations
python manage.py migrate --noinput --settings=gee_bridge.settings

# collect static files
python manage.py collectstatic --noinput --settings=gee_bridge.settings

# load admin
python manage.py loaddata admin.json --settings=gee_bridge.settings

# install dev deps if debugging
if [ $DEBUG = "1" ]
    then
        pipenv install --verbose --system --dev
fi

exec "$@"