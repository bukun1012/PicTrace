from django import forms
from .models import Profile
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]


class CustomPasswordResetForm(PasswordResetForm):
    """自定義密碼重置表單，處理郵件發送邏輯"""

    def save(
        self,
        domain_override=None,
        subject_template_name="users/password_reset_subject.txt",
        email_template_name="users/password_reset_email.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=settings.DEFAULT_FROM_EMAIL,
        request=None,
        **kwargs
    ):

        for user in self.get_users(self.cleaned_data["email"]):
            context = {
                "email": self.cleaned_data["email"],
                "domain": settings.DEFAULT_DOMAIN,
                "protocol": settings.PROTOCOL,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": token_generator.make_token(user),
            }
            subject = render_to_string(subject_template_name, context).strip()
            html_message = render_to_string(email_template_name, context)

            # 發送郵件
            email_msg = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=from_email,
                to=[self.cleaned_data["email"]],
            )
            email_msg.content_subtype = "html"
            email_msg.send()
