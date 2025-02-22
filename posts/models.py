from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    content = models.TextField()  # ✅ 內容（必填）
    image_url = models.URLField(max_length=500)  # ✅ 圖片 URL（必填）
    location = models.CharField(
        max_length=255, blank=True, null=True
    )  # ✅ 地點（選填，未來支援 Google Maps）
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 關聯到用戶
    created_at = models.DateTimeField(auto_now_add=True)  # 自動記錄建立時間

    def __str__(self):
        return f"{self.author.username} 的貼文 - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
