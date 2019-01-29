from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsHigherUserOrOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or request.user in obj.parents or request.user == obj
