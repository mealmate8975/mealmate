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

class Invitation(models.Model):

    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, '초대 수락 대기중'),
        (ACCEPTED, '초대 수락됨'),
        (REJECTED, '초대 거절됨'),
    ]

    # 초대를 보낸 채팅방
    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE
    )

    # 초대를 보낸 유저
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='sent_invitation',
        on_delete=models.CASCADE
    )
    # 초대를 받은 유저
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_invitation',
        on_delete=models.CASCADE
    )
    # 초대 상태
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    invited_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # soft delete 개념으로 나중에 초대를 취소하는 기능 구현 시 유용
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('chatroom','from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({self.status})"
    
class InvitationBlock(models.Model):
    blocking_user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    blocked_chatroom = models.ForeignKey(ChatRoom,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('blocking_user', 'blocked_chatroom')

    def __str__(self):
        return f"{self.blocking_user} blocked chatroom {self.blocked_chatroom.id}"
