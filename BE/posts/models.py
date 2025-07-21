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
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.page.name} - {self.type}"