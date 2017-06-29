from __future__ import unicode_literals

from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'
    verbose_name = "My App"

    def ready(self):
        import jsonfield_compat
        jsonfield_compat.register_app(self)
