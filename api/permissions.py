from rest_framework.permissions import BasePermission
from .models import Rasterbucket


class IsOwner(BasePermission):
    """Custom permission class to allow rasterbucket owners to edit them."""

    def has_object_permission(self, request, view, obj):
        """Return True if permission is granted to the rasterbucket owner."""
        if isinstance(obj, Rasterbucket):
            return obj.owner == request.user
        return obj.owner == request.user
