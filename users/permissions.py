from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import User, UserGroup


class UserOwnProfileOrReadOnly(permissions.BasePermission):
    """Limits profile editing to owner only."""

    def has_object_permission(
        self, request: Request, view: APIView, obj: User
    ) -> bool:
        if (
            obj.pk == request.user.pk
            or request.method in permissions.SAFE_METHODS
        ):
            return True
        return False


class UserGroupPermission(permissions.BasePermission):
    def has_object_permission(
        self, request: Request, view: APIView, obj: UserGroup
    ) -> bool:
        return super().has_object_permission(request, view, obj)
