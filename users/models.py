from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import CustomUserManager


class User(AbstractUser):
    objects = CustomUserManager()
    email = models.EmailField(unique=True)
    birth_date = models.DateField(blank=True, null=True)
    friends = models.ManyToManyField('self', blank=True)
    profile_picture = models.ImageField(
        default='default-profile-pic.png',
        upload_to='profile-pics/',
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.username})"

    class Meta:
        ordering = ['email']


class UserGroup(models.Model):
    name = models.TextField(max_length=255)
    administrators = models.ManyToManyField(User, related_name='groups_admin')
    members = models.ManyToManyField(User, related_name='groups_member')

    def __str__(self) -> str:
        return self.name
