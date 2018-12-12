FROM python:3.6-alpine

LABEL Author="francesco.bartoli@geobeyond.it"

# init
WORKDIR /tmp
COPY Pipfile /tmp/Pipfile
COPY Pipfile.lock /tmp/Pipfile.lock

# setup
RUN apk --update --no-cache add python3 py3-pip ca-certificates git wget bash linux-headers graphviz
RUN apk --update --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/main add openssl
# See https://github.com/appropriate/docker-postgis/blob/master/Dockerfile.alpine.template
# See https://hub.docker.com/r/dangerfarms/geodrf-alpine/~/dockerfile/
RUN apk --update --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ add \
  geos gdal proj4 protobuf-c postgresql-client gdal-dev jpeg-dev zlib-dev graphviz-dev geos-dev
# See https://www.merixstudio.com/blog/docker-multi-stage-builds-python-development/
RUN apk --upgrade --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/main add alpine-sdk
RUN apk --update add --virtual build-dependencies libffi-dev python3-dev \
  && apk add postgresql-dev \
  && ln -sf /usr/lib/libproj.so.13 /usr/lib/libproj.so \
  && ln -sf /usr/lib/libgdal.so.20 /usr/lib/libgdal.so \
  && ln -sf /usr/lib/libgeos_c.so.1 /usr/lib/libgeos_c.so \
  && pip3 install --upgrade pip \
  && pip3 install --upgrade pipenv \
  && pipenv install --verbose --system --deploy

# clean
RUN apk del build-dependencies
RUN apk del -r postgresql-libs postgresql-dev gdal-dev jpeg-dev zlib-dev geos-dev

# prep
ENV PYTHONUNBUFFERED 1
COPY . /app
WORKDIR /app

ENTRYPOINT [ "/app/entrypoint.sh" ]

CMD ["gunicorn", "-b", "0.0.0.0:8000", "--env", "DJANGO_SETTINGS_MODULE=gee_bridge.settings", "gee_bridge.wsgi", "--timeout 120"]