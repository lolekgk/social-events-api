from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from recurrence.fields import RecurrenceField


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
    class EventStatus(models.TextChoices):
        PLANNED = 'P', _('Planned')
        ONGOING = 'O', _('Ongoing')
        CANCELLED = 'C', _('Cancelled')
        ENDED = 'E', _('Ended')

    class EventAccess(models.TextChoices):
        OPEN = 'O', _('Open')
        INVITATION = 'I', _('Invitation')

    name = models.CharField(max_length=255)
    access = models.CharField(
        choices=EventAccess.choices, max_length=1, default=EventAccess.OPEN
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    organizers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='events_organizer'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='events_participant'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        choices=EventStatus.choices, max_length=1, default=EventStatus.PLANNED
    )
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    banner = models.ImageField(
        default='default-banner.jpeg',
        upload_to='event-banners/',
        null=True,
        blank=True,
    )
    recurrences = RecurrenceField(blank=True, null=True)
    # recurring events
    # https://django-recurrence.readthedocs.io/en/latest/index.html
    # group ? foreign key to the group of friends(users)

    def __str__(self) -> str:
        return self.name

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(
                'The end date of an event must be later than the start date.'
            )
