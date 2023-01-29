from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    birth_date = models.DateField()
    friends = models.ManyToManyField('self')
    profile_picture = models.ImageField(
        default='default-profile-pic.png',
        upload_to='profile-pics/',
        null=True,
        blank=True,
    )


class UserGroup(models.Model):
    name = models.TextField(max_length=255)
    administrators = models.ManyToManyField(User, related_name='groups_admin')
    members = models.ManyToManyField(User, related_name='groups_member')

    def __str__(self) -> str:
        return self.name
