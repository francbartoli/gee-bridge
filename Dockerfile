FROM python:3.6-alpine

LABEL Author="francesco.bartoli@geobeyond.it"

# init
WORKDIR /tmp
COPY Pipfile /tmp/Pipfile
COPY Pipfile.lock /tmp/Pipfile.lock

# setup
RUN apk --update --no-cache add python3 py3-pip ca-certificates git wget bash linux-headers graphviz
# See https://github.com/appropriate/docker-postgis/blob/master/Dockerfile.alpine.template
# See https://hub.docker.com/r/dangerfarms/geodrf-alpine/~/dockerfile/
RUN apk --update --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ add \
  geos gdal proj4 protobuf-c postgresql-client gdal-dev jpeg-dev zlib-dev graphviz-dev
RUN apk --update add --virtual build-dependencies gcc musl-dev libffi-dev python3-dev build-base \
# ISSUE https://github.com/Stanback/alpine-strongswan-vpn/pull/3
# TODO workaround start see https://github.com/pyca/cryptography/issues/4264
  && apk del libressl-dev \
  && apk add openssl-dev \
  && pip3 install cryptography==2.2.2 \
  && apk del openssl-dev \
  && apk add libressl-dev \
# TODO workaround end
  && apk add postgresql-dev \
  && pip3 install --upgrade pip \
  && pip3 install --upgrade pipenv \
  && pipenv install --verbose --system --deploy

# clean
RUN apk del build-dependencies
RUN apk del -r postgresql-libs postgresql-dev gdal-dev jpeg-dev zlib-dev

# prep
ENV PYTHONUNBUFFERED 1
COPY . /app
WORKDIR /app

ENTRYPOINT [ "/app/entrypoint.sh" ]

CMD ["gunicorn", "-b", "0.0.0.0:8000", "--env", "DJANGO_SETTINGS_MODULE=gee_bridge.settings", "gee_bridge.wsgi", "--timeout 120"]