from rest_framework import serializers

from .models import User, UserGroup


class UserPublicProfileSerializer(serializers.ModelSerializer):
    def to_representation(self, instance: User):
        current_user = self.context["request"].user
        is_friend = current_user.friends.filter(pk=instance.pk).exists()
        if is_friend:
            self.fields["friends"] = serializers.PrimaryKeyRelatedField(
                queryset=User.objects.all(), many=True
            )
        return super().to_representation(instance)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "profile_picture",
            "birth_date",
        ]


class UserOwnProfileRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = UserPublicProfileSerializer.Meta.fields + ["email"]


class UserOwnProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "profile_picture",
            "friends",
            "birth_date",
        ]
