from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Adds lightweight profile fields on top of Django's built-in user model.
    """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    height = models.PositiveSmallIntegerField(blank=True, null=True)
    weight = models.PositiveSmallIntegerField(blank=True, null=True)
    pregnancy = models.BooleanField(blank=True, null=True)
    disease_history = models.TextField(blank=True)

    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자"

    def __str__(self) -> str:
        return self.username or self.email


class ChatSession(models.Model):
    """
    Tracks a chat conversation, initially keyed by an anonymous session and
    later linked to a user once they log in.
    """
    session_key = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="chat_sessions",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "대화 세션"
        verbose_name_plural = "대화 세션"

    def __str__(self) -> str:
        if self.user:
            return f"{self.user}의 세션"
        return f"익명 세션({self.session_key})"


class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "사용자"
        ASSISTANT = "assistant", "어시스턴트"
        SYSTEM = "system", "시스템"

    session = models.ForeignKey(
        ChatSession,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "대화 메시지"
        verbose_name_plural = "대화 메시지"

    def __str__(self) -> str:
        return f"{self.get_role_display()}@{self.created_at:%Y-%m-%d %H:%M}"
