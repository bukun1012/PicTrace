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

    # 加入計算愛心數的屬性
    @property
    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.author.username} 的貼文 - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# 新增 Like 模型
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")  # ✅ 確保同一個用戶只能對一篇貼文按一次愛心

    def __str__(self):
        return f"{self.user.username} liked {self.post.id}"
