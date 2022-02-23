from rest_framework.permissions import BasePermission


class UserViewPermission(BasePermission):
    """
    Allows access to POST method to any user.
    Allows access to other methods only to authenticated users
    """
    def has_permission(self, request, view):
        return bool(request.method == 'POST' or (request.user and request.user.is_authenticated))
