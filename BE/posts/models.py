from django.db import models
from pages.models import Page
from accounts.models import CustomUser

class Post(models.Model):
    TYPE_CHOICES = [
        ('promo', '홍보'),
        ('review', '후기'),
        ('tip', '꿀TIP'),
    ]

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='posts',blank=True,null=True)
    content = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES,blank=True,null=True) # Django가 빈 문자열을 None으로 변환, DB에는 NULL이 저장됨
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.page.name} - {self.type}"
    
    def like_count(self):
        '''
        Post 모델에 좋아요 개수 쉽게 가져오는 헬퍼 메서드
        '''
        return self.likes.count()

class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # 한 유저가 한 포스트에 중복 좋아요 못 하게 함

    def __str__(self):
        return f"{self.user.email} liked {self.post.id}"