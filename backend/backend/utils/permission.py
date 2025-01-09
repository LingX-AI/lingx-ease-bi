from rest_framework.permissions import BasePermission


class IsOwnerPermission(BasePermission):
    """
    Custom permission to check if the user is the owner of the object
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
