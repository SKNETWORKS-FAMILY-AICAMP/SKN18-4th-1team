import json
from django.shortcuts import render
from user_app.models import ChatMessage, ChatSession
from .services import analyze_symptoms

# _format_result_for_log는 최종 출력 형식이 dic -> str로 된 관계로 삭제했습니다

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
                # 1. LangGraph가 생성한 '문자열' 답변을 받습니다.
                result = analyze_symptoms(symptoms)
                # 2. 사용자 질문 저장
                _store_message(request, ChatMessage.Role.USER, symptoms)
                # 3. [수정됨] 포맷팅 없이 결과 문자열을 그대로 저장합니다.
                _store_message(
                    request,
                    ChatMessage.Role.ASSISTANT,
                    result # _format_result_for_log 없이 바로
                )
            except Exception as e:
                error = f'분석 중 오류가 발생했습니다: {str(e)}'
    
    context = {
        'symptoms': symptoms,
        'result': result,
        'error': error,
    }
    
    return render(request, 'medical_app/index.html', context)


def home(request):
    """랜딩 페이지"""
    return render(request, 'medical_app/home.html')

