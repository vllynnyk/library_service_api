from rest_framework.permissions import BasePermission


class IsAdminOrOwnerPermission(BasePermission):
    """The request is restrict data for user,
    if as admin - all data is returned."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user