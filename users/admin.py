from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Tuple

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count, F, QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from .models import User, UserGroup


class AgeMajority(Enum):
    NONADULT = "<18"
    ADULT = ">18"


class AgeFilter(admin.SimpleListFilter):
    title = "age"
    parameter_name = "age"

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:

        return [
            (AgeMajority.NONADULT.value, "Nonadult"),
            (AgeMajority.ADULT.value, "Adult"),
        ]

    def queryset(
        self, request: Any, queryset: QuerySet[Any]
    ) -> Optional[QuerySet[Any]]:
        if self.value() == AgeMajority.NONADULT.value:
            return queryset.filter(age__lt=18)
        elif self.value() == AgeMajority.ADULT.value:
            return queryset.filter(age__gt=18)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "username",
        "email",
        "full_name",
        "friends_count",
        "age",
        "profile_picture",
        "is_staff",
    ]
    list_editable = ["profile_picture", "is_staff"]
    list_per_page = 10
    list_filter = [
        "date_joined",
        AgeFilter,
        "groups_member",
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    ]
    ordering = ["first_name", "last_name"]
    search_fields = [
        "first_name__istartswith",
        "last_name__istartswith",
        "email__istartswith",
    ]
    autocomplete_fields = ["friends"]

    # fields in 'edit' panel
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
                    "friends",
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

    # fields in 'add' panel
    add_fieldsets = (
        (
            (None),
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

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return (
            super()
            .get_queryset(request)
            .annotate(
                friends_count=Count("friends"),
                age=datetime.now().year - F("birth_date__year"),
            )
        )

    @admin.display(ordering="friends_count")
    def friends_count(self, user: User):
        url = (
            reverse("admin:users_user_changelist")
            + "?"
            + urlencode({"friends__id": str(user.id)})
        )
        return format_html('<a href="{}">{}</a>', url, user.friends_count)

    @admin.display(ordering="age")
    def age(self, user: User):
        return user.age

    @admin.display(ordering="full_name")
    def full_name(self, user: User):
        return user.get_full_name()


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "members_count"]
    list_per_page = 10
    search_fields = ["name__istartswith"]
    ordering = ["name"]
    autocomplete_fields = ["administrators", "members"]

    @admin.display(ordering="members_count")
    def members_count(self, user_group: UserGroup):
        # go to the Users list
        url = (
            reverse("admin:users_user_changelist")
            + "?"
            + urlencode({"groups_member__id": str(user_group.id)})
        )
        return format_html(
            '<a href="{}">{}</a>', url, user_group.members_count
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return (
            super()
            .get_queryset(request)
            .annotate(members_count=Count("members"))
        )
