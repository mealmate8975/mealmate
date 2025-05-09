from django.db import models
from django.conf import settings

class Friendship(models.Model):

    STATUS_CHOICES = [
        ('pending', '수락 대기중'),
        ('accepted', '수락됨'),
        ('rejected', '거절됨'),
    ]
    # 친구 요청을 보낸 유저
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='sent_friend_request',
        on_delete=models.CASCADE
    )
    # 친구 요청을 받은 유저
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_friend_request',
        on_delete=models.CASCADE
    )
    # 요청 상태
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    requested_at = models.DateTimeField(auto_now_add=True),
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({self.status})"