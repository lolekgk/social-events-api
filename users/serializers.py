from rest_framework import serializers

from .models import User, UserGroup


class UserProfileSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context["request"]

        if not (
            request.user.is_authenticated and request.user == self.instance
        ):
            # TODO add group_member, and group_admin

            self.fields.pop("email")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "profile_picture",
            "birth_date",
            "friends",
            "email",
        ]
        read_only_fields = ["id", "username", "email"]


class UserGroupSerializer(serializers.ModelSerializer):
    administrators = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True
    )
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True
    )

    class Meta:
        model = UserGroup
        fields = ["id", "name", "description", "administrators", "members"]
        read_only_fields = ["id"]
