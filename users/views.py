from rest_framework import viewsets

from .models import User
from .permissions import UserOwnProfileOrReadOnly
from .serializers import UserOwnProfileSerializer, UserPublicProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    GET(retrieve): Retrieve user's profile.

    PUT/PATCH: Update current user's profile.

    DELETE: Mark current user's profile as not active.
    """

    queryset = User.objects.all()
    permission_classes = [UserOwnProfileOrReadOnly]

    def get_serializer_class(self):
        serializer_classes = {
            "list": UserPublicProfileSerializer,
            "retrieve": UserOwnProfileSerializer
            if self.get_object().pk == self.request.user.pk
            else UserPublicProfileSerializer,
        }
        return serializer_classes.get(self.action, UserOwnProfileSerializer)

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
