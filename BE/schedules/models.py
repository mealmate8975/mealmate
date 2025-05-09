from django.db import models
from restaurants.models import restaurant
from accounts.models import CustomUser

class Schedules(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    rest_id = models.ForeignKey(restaurant,null=True,on_delete=models.DO_NOTHING)
    created_by = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING)

    schedule_name = models.CharField(null=True,max_length=100,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    schedule_at = models.DateTimeField(null=True,blank=True)
    schedule_condition = models.JSONField(null=True,blank=True)