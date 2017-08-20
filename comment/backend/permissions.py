from rest_framework import permissions
from django.utils.translation import ugettext_lazy as _


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = _('Only owner can edit or delete instances')

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        is_owner = obj.user_id == request.data.get('user_id', None)
        return is_owner


class IsLeafNodeOrNotDelete(permissions.BasePermission):
    message = _('Only leaf nodes may be deleted')

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return obj.is_leaf_node
        return True
