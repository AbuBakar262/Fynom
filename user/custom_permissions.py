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