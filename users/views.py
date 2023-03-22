from rest_framework import viewsets
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from .models import User
from .permissions import UserOwnProfileOrReadOnly
from .serializers import (
    UserOwnProfileRetrieveSerializer,
    UserOwnProfileUpdateSerializer,
    UserPublicProfileSerializer,
)


class UserDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve user's profile.

    PUT/PATCH: Update current user's profile.
    """

    queryset = User.objects.all()
    permission_classes = [UserOwnProfileOrReadOnly]

    def get_serializer_class(self):
        if self.kwargs["pk"] != self.request.user.pk:
            return UserPublicProfileSerializer
        if self.request.method in ["PUT", "PATCH"]:
            return UserOwnProfileUpdateSerializer
        return UserOwnProfileRetrieveSerializer

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
