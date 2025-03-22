from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user == view.request.user

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsSuperUserOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if hasattr(view.request.user, "role"):
            return (
                view.request.user.is_superuser
                or view.request.user.role == "admin"
            )
        else:
            return view.request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if hasattr(view.request.user, "role"):
            return (
                view.request.user.is_superuser
                or view.request.user.role == "admin"
            )
        else:
            return view.request.user.is_superuser


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user == view.request.user

    def has_object_permission(self, request, view, obj):
        if hasattr(view.request.user, "role"):
            return (
                view.request.user.is_superuser
                or view.request.user.role == "admin"
            )
        else:
            return view.request.user.is_superuser


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
