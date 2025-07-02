from django.db import models
from django.conf import settings
from schedules.models import Schedules

class Participants(models.Model):
    schedule = models.ForeignKey(
        Schedules,
        on_delete=models.CASCADE,
        related_name="participants"
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        # on_delete= models.SET_NULL,
        on_delete= models.CASCADE,
        default=None,
        # null=True,
        # blank=True
    )
    is_host = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('schedule', 'participant')