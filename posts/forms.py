from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    image = forms.FileField(required=True, label="圖片")  # ✅ 圖片為必填

    class Meta:
        model = Post
        fields = ["content", "image", "location"]  # ✅ 只保留內容、圖片和地點
        widgets = {
            "content": forms.Textarea(attrs={"placeholder": "說點什麼...", "rows": 4}),
            "location": forms.TextInput(attrs={"placeholder": "新增地點（選填）"}),
        }
