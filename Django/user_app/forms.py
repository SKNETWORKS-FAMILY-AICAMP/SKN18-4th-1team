from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm

User = get_user_model()


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    """
    Extends Django's default AuthenticationForm to accept either a username
    or an email address in the username field.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "아이디 또는 이메일"
        self.fields['password'].label = "비밀번호"

    def clean(self):
        username = self.cleaned_data.get('username')
        if username and '@' in username:
            try:
                user = User._default_manager.get(email__iexact=username)
            except User.DoesNotExist:
                pass
            else:
                self.cleaned_data['username'] = user.get_username()
        return super().clean()


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
