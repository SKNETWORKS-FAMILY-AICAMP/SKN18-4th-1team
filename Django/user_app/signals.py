from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import ChatSession


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

    chat_session = ChatSession.objects.filter(session_key=session_key).first()
    if chat_session is None:
        has_summary = bool(request.session.get('chat_memory_summary'))
        if not has_summary:
            # 아직 저장할 상담 요약이 없으면 세션을 만들지 않는다.
            return
        chat_session = ChatSession.objects.create(
            session_key=session_key,
            user=user,
        )
    elif chat_session.user_id is None:
        chat_session.user = user
        chat_session.save(update_fields=['user'])
    else:
        if chat_session.user_id != user.id:
            chat_session.user = user
            chat_session.save(update_fields=['user'])
