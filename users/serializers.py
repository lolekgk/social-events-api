from rest_framework import serializers

from .models import User, UserGroup


class UserPublicProfileSerializer(serializers.ModelSerializer):
    friends = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "profile_picture",
            "friends",
            "birth_date",
        ]


class UserOwnProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = UserPublicProfileSerializer.Meta.fields + ["email"]
