from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

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

    queryset = User.objects.all()
    permission_classes = [UserOwnProfileOrReadOnly]
    pagination_class = DefaultPagination
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["first_name", "last_name"]

    def get_queryset(self):
        return self.queryset.filter(is_active=True)

    def perform_destroy(self, instance: User) -> None:
        instance.is_active = False
        instance.save()


@extend_schema(tags=["user groups"])
class UserGroupViewSet(viewsets.ModelViewSet):

    queryset = UserGroup.objects.all()
    permission_classes = [IsAuthenticated, UserGroupPermission]
    serializer_class = UserGroupSerializer

    def get_queryset(self):
        return self.queryset.filter(is_deleted=False)


# * List current user groups
# * Do not show id of inactive users as a members/admin
# * What should happen with a group if the only one admin deletes a profile

# TODO add usergroups detail view
# TODO add current user usergrups list view
# TODO add current user friends list view with min. user info?
# TODO friends_invitation, group invitation
# TODO invitation list and detail view
