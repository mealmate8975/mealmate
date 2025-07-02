from django.db import models
from restaurants.models import Restaurant
from accounts.models import CustomUser

class Schedules(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    rest_id = models.ForeignKey(Restaurant,null=True,on_delete=models.DO_NOTHING)
    created_by = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING)

    schedule_name = models.CharField(null=True,max_length=100,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # schedule_at = models.DateTimeField(null=True,blank=True)
    schedule_condition = models.JSONField(null=True,blank=True)

    # 약속 시간 취합을 위해 필요한 필드 수정 및 추가
    schedule_start = models.DateTimeField(null=True,blank=True)
    schedule_end = models.DateTimeField(null=True,blank=True)

    is_meal = models.BooleanField(default=True) # 식사 약속 여부
    is_chatroom = models.BooleanField(default=False) # 채팅방 여부