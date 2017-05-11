from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Rasterbucket, Process


class IsOwner(BasePermission):
    """Custom permission class to allow rasterbucket owners to edit them."""

    def has_object_permission(self, request, view, obj):
        """Return True if permission is granted to the rasterbucket owner."""
        if isinstance(obj, Rasterbucket):
            return obj.owner == request.user
        return obj.owner == request.user
        """Return True if permission is granted to the process owner."""
        if isinstance(obj, Process):
            return obj.owner == request.user
        return obj.owner == request.user


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user
