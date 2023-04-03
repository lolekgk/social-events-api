from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import User, UserGroup
from .pagination import DefaultPagination
from .permissions import UserGroupPermission, UserOwnProfileOrReadOnly
from .serializers import UserGroupSerializer, UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    GET (list): Retrieve a list of active users.

    GET(retrieve): Retrieve user's profile.

    PUT/PATCH: Update current user's profile.

    DELETE: Mark current user's profile as not active.
    """

    permission_classes = [UserOwnProfileOrReadOnly]
    pagination_class = DefaultPagination
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["first_name", "last_name"]

    def get_queryset(self):
        return User.objects.filter(is_active=True)

    def perform_destroy(self, instance: User) -> None:
        instance.perform_soft_delete()


@extend_schema(tags=["user groups"])
class UserGroupViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, UserGroupPermission]
    pagination_class = DefaultPagination
    serializer_class = UserGroupSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        request.data["members"].append(request.user.id)
        request.data["administrators"].append(request.user.id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_queryset(self):
        filtered_users = User.objects.exclude(is_active=False)
        return (
            UserGroup.objects.filter(is_deleted=False)
            .filter(members=self.request.user)
            .prefetch_related(
                Prefetch("members", queryset=filtered_users),
                Prefetch("administrators", queryset=filtered_users),
            )
        )

    def perform_destroy(self, instance: UserGroup) -> None:
        instance.perform_soft_delete()


# * What should happen with a group if the only one admin deletes a profile

# TODO add current user friends list view with min. user info?
# TODO friends_invitation, group invitation
# TODO invitation list and detail view
