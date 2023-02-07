from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from .models import User, UserGroup


# TODO add users's friends to admin panel
# TODO add age to filtering
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "get_friends",
        "birth_date",
        "profile_picture",
        "is_staff",
    )

    fieldsets = (
        ("Sign-in data", {"fields": ("username", "password")}),
        (
            ("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "birth_date",
                    "profile_picture",
                )
            },
        ),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "email",
                    "first_name",
                    "last_name",
                    "birth_date",
                    "friends",
                    "profile_picture",
                ),
            },
        ),
    )
    # todo
    def get_friends(self, obj):
        return [friend for friend in obj.friends.all()]


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'members_count']

    @admin.display(ordering='members_count')
    def members_count(self, user_group: UserGroup):
        # go to the Users list
        url = (
            reverse('admin:users_user_changelist')
            + '?'
            + urlencode({'groups_member__id': str(user_group.id)})
        )
        return format_html(
            '<a href="{}">{}</a>', url, user_group.members_count
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return (
            super()
            .get_queryset(request)
            .annotate(members_count=Count('members'))
        )
