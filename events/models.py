from django.core.exceptions import ValidationError
from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=75)
    country = models.CharField(max_length=75)
    city = models.CharField(max_length=75)
    street = models.CharField(max_length=75)
    street_number = models.CharField(max_length=10)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    # added_by? foreign key to the user

    def __str__(self) -> str:
        return self.name


class Event(models.Model):
    class EventStatus(models.TextChoices):
        PLANNED = 'P'
        ONGOING = 'O'
        CANCELLED = 'C'
        ENDED = 'E'

    # access? it's open or we need to have an invitation

    name = models.CharField(max_length=255)  # should it be unique?
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # group ? foreign key to the group of friends(users)
    # organisers -> manytomany field to users
    # participants -> same
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        choices=EventStatus.choices, max_length=1, default=EventStatus.PLANNED
    )
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    # recurring event

    def __str__(self) -> str:
        return self.name

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(
                'The end date of an event must be later than the start date.'
            )


# Create separate app for the Users?
