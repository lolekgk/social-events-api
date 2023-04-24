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

    GET(retrieve): Retrieve a specific user's profile by their ID.

    PUT/PATCH: Update current user's profile. Users can only update their own profiles.

    DELETE: Mark current user's profile as not active. Users can only delete their own profiles.
    """

    http_method_names = ["get", "put", "patch", "delete", "options", "head"]
    permission_classes = [UserOwnProfileOrReadOnly]
    pagination_class = DefaultPagination
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["first_name", "last_name"]

    def get_queryset(self):
        return User.objects.filter(is_active=True)


@extend_schema(tags=["user groups"])
class UserGroupViewSet(viewsets.ModelViewSet):
    """
    GET (list): Retrieve a list of User Groups the current user is a member of, excluding deleted groups.

    GET (retrieve): Retrieve a specific User Group by its ID, along with its members and administrators.

    POST (create): Create a new User Group. The current user will be automatically added as a member and administrator.

    PUT/PATCH (update): Update the details of a User Group, such as its name or description. Only administrators can update a User Group.

    DELETE: Soft-delete a User Group, marking it as deleted. Only administrators can delete a User Group.
    """

    permission_classes = [IsAuthenticated, UserGroupPermission]
    pagination_class = DefaultPagination
    serializer_class = UserGroupSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "members__username"]
    ordering_fields = ["name"]

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
