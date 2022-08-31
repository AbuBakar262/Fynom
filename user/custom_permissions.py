from rest_framework import permissions

class IsApprovedUser(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.status == 'Approved':
            return True
        return False

class IsNotSuspendUser(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.status != 'Suspend':
            return True
        return False

class IsNotBlockedUser(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.status != 'Block':
            return True
        return False


class IsPostOrIsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        # allow all POST requests
        if request.method == 'POST':
            return True

        # Otherwise, only allow authenticated requests
        # Post Django 1.10, 'is_authenticated' is a read-only attribute
        return request.user and request.user.is_authenticated


class IsEmailExist(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.email:
            return True
        return False