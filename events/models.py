from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from recurrence.fields import RecurrenceField

from users.models import UserGroup

from .constants import EventStatus, EventType


class Location(models.Model):
    name = models.CharField(max_length=75)
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    country = models.CharField(max_length=75, blank=True, null=True)
    city = models.CharField(max_length=75, blank=True, null=True)
    street = models.CharField(max_length=75, blank=True, null=True)
    street_number = models.CharField(max_length=10, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(
        choices=EventType.choices, max_length=1, default=EventType.OPEN
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    organizers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="events_organizer"
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="events_participant"
    )
    group = models.ForeignKey(
        UserGroup,
        default=None,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        choices=EventStatus.choices, max_length=1, default=EventStatus.PLANNED
    )
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="events"
    )
    banner = models.ImageField(
        default="default-banner.jpeg",
        upload_to="event-banners/",
        null=True,
        blank=True,
    )
    recurrences = RecurrenceField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.start_time >= self.end_time:
            raise ValidationError(
                "The end date of an event must be later than the start date."
            )


# TODO create abstract invitation for: eventINV, friendsINV, groupINV
class EventInvitation(models.Model):
    class InvitationStatus(models.TextChoices):
        ACCEPTED = "A", _("Accepted")
        DECLINED = "D", _("Declined")
        PENDING = "P", _("Pending")

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_invitations",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="invited_users",
    )
    status = models.CharField(
        choices=InvitationStatus.choices,
        max_length=1,
        default=InvitationStatus.PENDING,
    )
