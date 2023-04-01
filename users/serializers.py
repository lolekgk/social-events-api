from rest_framework import serializers

from .models import User, UserGroup


class UserProfileSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context["request"]

        if not (
            request.user.is_authenticated and request.user == self.instance
        ):
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
