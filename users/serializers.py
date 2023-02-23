from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers

from .models import User


class UserCreateSerializer(BaseUserCreateSerializer):
    profile_picture = serializers.ImageField(default='default-profile-pic.png')

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = [
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'birth_date',
            'profile_picture',
        ]


class CurrentUserSerializer(UserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = UserCreateSerializer.Meta.fields + [
            'friends',
            'groups_member',
            'groups_admin',
            'date_joined',
        ]
