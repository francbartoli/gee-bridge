# -*- coding: utf-8 -*-
"""Summary
"""
from rest_framework.compat import coreapi
from rest_framework.filters import BaseFilterBackend


def additional_schema(schema):
    """
    rest framework does not provide a way to override the schema on
    a per endpoint basis.  this is a cheap way to get the fields to
    appear on the swagger web interface through the filter_backends

    Args:
        schema (TYPE): Description
    """
    class SwaggerFilterBackend(object):
        """Summary
        """
        def get_schema_fields(self, view):
            """Summary

            Args:
                view (TYPE): Description

            Returns:
                TYPE: Description
            """
            keys = ('name', 'required', 'location', 'type', 'description')
            return [
                coreapi.Field(**{
                    key: val for key, val in field.items() if key in keys})
                for field in schema.values()
            ]

        def filter_queryset(self, request, queryset, view):
            """Summary

            Args:
                request (TYPE): Description
                queryset (TYPE): Description
                view (TYPE): Description

            Returns:
                TYPE: Description
            """
            # do nothing
            return queryset

    def wrapper(cls):
        """Summary

        Returns:
            TYPE: Description
        """
        cls.filter_backends = (BaseFilterBackend, )
        cls.filter_backends = list(cls.filter_backends) + [SwaggerFilterBackend]
        return cls

    return wrapper
