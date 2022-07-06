from rest_framework import permissions

class IsApprovedUser(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.status == 'Approve':
            return True
        return False