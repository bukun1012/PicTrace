from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=255)  # 貼文標題
    content = models.TextField()  # 內容
    image_url = models.URLField(max_length=500, blank=True, null=True)  # 存 S3 URL
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 關聯到用戶
    created_at = models.DateTimeField(auto_now_add=True)  # 自動記錄建立時間

    def __str__(self):
        return self.title
