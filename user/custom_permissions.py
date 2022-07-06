from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsApprovedUser(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.status == 'Approve':
            return True
        return False

