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

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)

        # 如果是新增貼文，圖片為必填；編輯貼文時圖片為非必填
        if not self.instance.pk:
            self.fields["image"].required = True
        else:
            self.fields["image"].required = False
