from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import User, UserGroup


class UserOwnProfileOrReadOnly(permissions.BasePermission):
    """Limits profile editing to owner."""

    def has_object_permission(
        self, request: Request, view: APIView, obj: User
    ) -> bool:
        if request.method not in permissions.SAFE_METHODS:
            return obj.pk == request.user.pk
        return True


class UserGroupPermission(permissions.BasePermission):
    """Limits user group access to their members (safe methods only) and administrators"""

    def has_permission(self, request: Request, view: APIView) -> bool:
        user_id = view.kwargs.get("user_pk")
        return str(request.user.id) == user_id

    def has_object_permission(
        self, request: Request, view: APIView, obj: UserGroup
    ) -> bool:
        if request.user in obj.members.all():
            return request.method in permissions.SAFE_METHODS
        return request.user in obj.administrators.all()
