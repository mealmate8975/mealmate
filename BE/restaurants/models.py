from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class Restaurant(models.Model):
    cuisine_choices = [
    ('KR', '한식'),
    ('CN', '중식'),
    ('JP', '일식'),
    ('IT', '이탈리안'),
    ('FR', '프렌치'),
    ('TH', '태국'),
    ('VN', '베트남'),
    ('ET', '기타')
    ]

    rest_id = models.AutoField(primary_key=True)
    rest_name = models.CharField(max_length=150)
    rest_cuisine = models.CharField(choices=cuisine_choices, max_length=2, default='ET',null=False)
    rest_address = models.CharField(max_length=255)
    rest_contact = PhoneNumberField(
        blank=True,
        null=True,      
        region='KR',    # 기본 국가 코드
    )  
