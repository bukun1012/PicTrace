from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    image = forms.FileField(required=False)  # ✅ 允許上傳圖片

    class Meta:
        model = Post
        fields = ["title", "content"]  # ❌ 移除 image，因為資料庫沒有這個欄位
