from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsAuthenticatedOrRead(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return super(IsAuthenticatedOrRead, self).has_permission(request, view)
