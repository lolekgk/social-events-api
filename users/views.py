from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import User
from .pagination import DefaultPagination
from .permissions import UserOwnProfileOrReadOnly
from .serializers import UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
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

    def perform_destroy(self, instance: User) -> None:
        instance.is_active = False
        instance.save()


class UserGroupsViewSet(viewsets.ModelViewSet):
    pass


# TODO add usergroups detail view
# TODO add current user usergrups list view
# TODO add current user friends list view with min. user info?
# TODO friends_invitation, group invitation
# TODO invitation list and detail view
