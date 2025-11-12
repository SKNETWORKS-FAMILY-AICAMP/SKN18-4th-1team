from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "name", "nickname")
        labels = {
            "username": "아이디",
            "email": "이메일",
            "name": "이름",
            "nickname": "닉네임",
        }
        help_texts = {
            "username": "",
        }


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ("name", "email", "nickname")
        labels = {
            "name": "이름",
            "email": "이메일",
            "nickname": "닉네임",
        }
