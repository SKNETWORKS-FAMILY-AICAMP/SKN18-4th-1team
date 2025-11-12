import json

from django.shortcuts import render

from user_app.models import ChatMessage, ChatSession

from .services import analyze_symptoms


def _format_result_for_log(result: dict) -> str:
    """Convert the analysis payload into a readable text block for history."""
    lines = []
    for disease in result.get('diseases', []):
        lines.append(f"[질병] {disease['name']}: {disease['description']}")
        if disease.get('recommendations'):
            for tip in disease['recommendations']:
                lines.append(f"  - {tip}")
    for hospital in result.get('hospitals', []):
        lines.append(
            f"[병원] {hospital['name']} ({hospital.get('specialty', '')}) - {hospital.get('address', '')}"
        )
    if not lines:
        lines.append(json.dumps(result, ensure_ascii=False))
    return "\n".join(lines)


def _get_or_create_session_for_user(request):
    if not request.session.session_key:
        request.session.save()

    chat_session, _ = ChatSession.objects.get_or_create(
        session_key=request.session.session_key,
        defaults={'user': request.user},
    )

    if chat_session.user_id is None and request.user.is_authenticated:
        chat_session.user = request.user
        chat_session.save(update_fields=['user'])

    return chat_session


def _store_message(request, role, content):
    """
    로그인 상태면 DB에, 아니면 세션에 기록하여 새로고침 시에는 사라지지만
    로그인 후에는 시그널이 DB로 옮길 수 있게 한다.
    """
    if request.user.is_authenticated:
        chat_session = _get_or_create_session_for_user(request)
        ChatMessage.objects.create(session=chat_session, role=role, content=content)
    else:
        history = request.session.get('chat_history', [])
        history.append({'role': role, 'content': content})
        request.session['chat_history'] = history
        request.session.modified = True


def index(request):
    """메인 페이지 뷰 - 증상 입력 및 분석 결과 표시 (순수 Django 서버 사이드 렌더링)"""
    result = None
    symptoms = ''
    error = None
    
    if request.method == 'POST':
        symptoms = request.POST.get('symptoms', '').strip()
        
        if not symptoms:
            error = '증상을 입력해주세요.'
        else:
            try:
                result = analyze_symptoms(symptoms)
                _store_message(request, ChatMessage.Role.USER, symptoms)
                _store_message(
                    request,
                    ChatMessage.Role.ASSISTANT,
                    _format_result_for_log(result),
                )
            except Exception as e:
                error = f'분석 중 오류가 발생했습니다: {str(e)}'
    
    if request.user.is_authenticated:
        chat_sessions = (
            ChatSession.objects.filter(user=request.user)
            .prefetch_related("messages")
            .order_by("-created_at")
        )
    else:
        chat_sessions = ChatSession.objects.none()

    context = {
        'symptoms': symptoms,
        'result': result,
        'error': error,
        'chat_sessions': chat_sessions,
    }
    
    return render(request, 'medical_app/index.html', context)


def home(request):
    """랜딩 페이지"""
    return render(request, 'medical_app/home.html')

