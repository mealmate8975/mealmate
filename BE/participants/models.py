from django.db import models
from django.conf import settings
from schedules.models import Schedules

# Create your models here.
class Participants(models.Model):
    schedule = models.ForeignKey(
        Schedules,
        on_delete=models.CASCADE,
        related_name="participants"
    )
    participants = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.SET_NULL,
        null=True,
        blank=True
    )