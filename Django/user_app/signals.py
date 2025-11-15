from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import ChatMessage, ChatSession


@receiver(user_logged_in)
def link_chat_session(sender, user, request, **kwargs):
    """
    로그인 직후 현재 세션에 쌓여 있던 익명 대화를 실제 사용자 계정으로 옮긴다.
    """
    if request is None:
        return

    if not request.session.session_key:
        request.session.save()

    session_key = request.session.session_key
    pending_history = request.session.pop('chat_history', None)

    chat_session = ChatSession.objects.filter(session_key=session_key).first()
    if chat_session is None:
        if not pending_history:
            return
        chat_session = ChatSession.objects.create(
            session_key=session_key,
            user=user,
        )
    elif chat_session.user_id is None:
        chat_session.user = user
        chat_session.save(update_fields=['user'])

    if pending_history:
        messages = [
            ChatMessage(
                session=chat_session,
                role=entry.get('role', ChatMessage.Role.USER),
                content=entry.get('content', ''),
            )
            for entry in pending_history
            if entry.get('content')
        ]
        ChatMessage.objects.bulk_create(messages)
        request.session.modified = True
