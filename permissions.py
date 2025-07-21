from rest_framework.permissions import BasePermission


class IsAdminAllOrIsAuthenticatedReadOnly(BasePermission):
    """The request is authenticated as an admin -read/write,
    if as user - read only request."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user