from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일 입력은 필수입니다.")
        if not password:
            raise ValueError("비밀번호 입력은 필수입니다.")
        email = self.normalize_email(email) # 이메일을 평문화합니다.EX) TeST@gmail.COM -> test@gmail.com
        user = self.model(email = email, **extra_fields) # user = CustomUser(email = ..., password = ...) 식으로 생성됨
        user.set_password(password) # 비밀번호 해시(hash)화
        user.save(using = self._db) # 연결된 db에 저장(_db)
        return user

class CustomUser(AbstractBaseUser):
    objects = CustomUserManager() # 유저 생성이랑 연결
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
    profile_image = models.ImageField(upload_to="profile_images/",blank=True,null=True,default="profile_images/default.jpeg")
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email' # 이메일로 로그인
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

# 유저 차단 테이블
class UserBlock(models.Model):
    blocker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blocker')
    blocked_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blocked_user')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blocker.email} blocked {self.blocked_user.email}"
