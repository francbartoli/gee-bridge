from __future__ import unicode_literals

from django.apps import AppConfig


class MapclientConfig(AppConfig):
    name = 'mapclient'

    # importing signals so they are available outside of the models
    def ready(self):
        from mapclient import signals
