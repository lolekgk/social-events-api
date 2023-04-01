from rest_framework import serializers

from .models import User, UserGroup


class UserPublicProfileSerializer(serializers.ModelSerializer):
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
        ]


class UserOwnProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = UserPublicProfileSerializer.Meta.fields + ["email"]
        read_only_fields = ["id", "username", "email"]
