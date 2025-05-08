from django.contrib.auth.models import AbstractBaseUser
from django.db import models

class CustomUser(AbstractBaseUser):

    GENDER_CHOICES = [
    ('0', 'Male'),
    ('1', 'Female'),
    ]

    # AbstractBaseUser는 자동으로 username을 아이디로 사용한다
    # 난 아이디를 이메일로 할것이라 username을 None으로 처리
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1)
    nickname = models.CharField(max_length=50, unique= True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    USERNAME_FIELD = 'email' # 이메일로 로그인
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
    
