# -*- coding: utf-8 -*-
from rest_framework.compat import coreapi
from rest_framework.filters import BaseFilterBackend


def additional_schema(schema):
    """
    rest framework does not provide a way to override the schema on
    a per endpoint basis.  this is a cheap way to get the fields to
    appear on the swagger web interface through the filter_backends
    """
    class SwaggerFilterBackend(object):

        def get_schema_fields(self, view):
            keys = ('name', 'required', 'location', 'type', 'description')
            return [
                coreapi.Field(**{
                    key: val for key, val in field.items() if key in keys})
                for field in schema.values()
            ]

        def filter_queryset(self, request, queryset, view):
            # do nothing
            return queryset

    def wrapper(cls):
        cls.filter_backends = (BaseFilterBackend, )
        cls.filter_backends = list(cls.filter_backends) + [SwaggerFilterBackend]
        return cls

    return wrapper
