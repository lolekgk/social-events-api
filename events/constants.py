from django.db import models
from django.utils.translation import gettext_lazy as _


class EventType(models.TextChoices):
    OPEN = "O", _("Open")
    PRIVATE = "P", _("Private")
    GROUP = "G", _("Group")


class EventStatus(models.TextChoices):
    PLANNED = "P", _("Planned")
    ONGOING = "O", _("Ongoing")
    CANCELLED = "C", _("Cancelled")
    ENDED = "E", _("Ended")
