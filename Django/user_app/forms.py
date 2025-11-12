from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "name")
        labels = {
            "username": "아이디",
            "email": "이메일",
            "name": "이름",
        }
        help_texts = {
            "username": "",
        }


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ("name", "email", "address", "height", "weight", "pregnancy", "disease_history")
        labels = {
            "name": "이름",
            "email": "이메일",
            "address": "주소",
            "height": "키(cm)",
            "weight": "몸무게(kg)",
            "pregnancy": "임신 여부",
            "disease_history": "기존 질병 이력",
        }
