from django.db import models

class Page(models.Model):
    # CATEGORY_CHOICES = [
    #     ('restaurant', '식당'),
    #     ('festival', '축제'),
    #     ('performance', '공연'),
    #     ('exhibition', '전시'),
    # ]

    name = models.CharField(max_length=100)
    description = models.JSONField(null=True,blank=True)
    # category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name