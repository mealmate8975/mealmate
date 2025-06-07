from django.db import models
from schedules.models import Schedules
from django.conf import settings

class ChatRoom(models.Model):
    schedule = models.OneToOneField(Schedules, on_delete=models.CASCADE, related_name="chatroom")

    def __str__(self):
        return f"ChatRoom for Schedule {self.schedule.schedule_id}"


class ChatParticipant(models.Model):
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("chatroom", "user")

    def __str__(self):
        return f"{self.user.nickname} in chatroom {self.chatroom.id}"