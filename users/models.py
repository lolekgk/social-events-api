from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    birth_date = models.DateField(blank=True, null=True)
    friends = models.ManyToManyField("self", blank=True)
    profile_picture = models.ImageField(
        default="default-profile-pic.png",
        upload_to="profile-pics/",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.username})"

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()

    class Meta:
        ordering = ["username"]


class UserGroup(models.Model):
    name = models.TextField(max_length=255)
    description = models.TextField(blank=True, null=True)
    administrators = models.ManyToManyField(User, related_name="groups_admin")
    members = models.ManyToManyField(User, related_name="groups_member")
    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()


class FriendInvitation:
    ...


class GroupInvitation:
    ...
