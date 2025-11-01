from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """Allow access only to the owner of the object."""

    def has_object_permission(self, request, view, obj):
        if obj == request.user:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False
