import json
from django.shortcuts import render
from user_app.models import ChatMessage, ChatSession
from .services import analyze_symptoms

# (헬퍼 함수들은 그대로 유지하거나 필요 시 수정)

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
    메시지 저장: 로그인(DB) / 비로그인(Session) 분기 처리
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
    """
    메인 뷰: 채팅 기록을 불러오고, 새로운 질문을 처리합니다.
    """
    error = None
    
    # 1. POST 요청 처리 (사용자가 질문을 보냈을 때)
    if request.method == 'POST':
        symptoms = request.POST.get('symptoms', '').strip()
        
        if not symptoms:
            error = '내용을 입력해주세요.'
        else:
            try:
                # (1) 사용자 질문 저장
                _store_message(request, ChatMessage.Role.USER, symptoms)
                
                # (2) AI 분석 수행 (services.py 호출)
                ai_response = analyze_symptoms(symptoms)
                
                # (3) AI 답변 저장
                _store_message(
                    request,
                    ChatMessage.Role.ASSISTANT,
                    ai_response
                )
            except Exception as e:
                error = f'오류가 발생했습니다: {str(e)}'

    # 2. 대화 기록 불러오기 (GET, POST 모두 실행)
    # 화면에 채팅창을 그려주기 위해 저장된 모든 대화를 가져옵니다.
    chat_history = []
    if request.user.is_authenticated:
        # 로그인 유저: DB에서 해당 세션의 메시지를 시간순으로 가져옴
        chat_session = _get_or_create_session_for_user(request)
        chat_history = ChatMessage.objects.filter(session=chat_session).order_by('id') 
        # (만약 models.py에 created_at이 있다면 .order_by('created_at')을 추천합니다)
    else:
        # 비로그인 유저: 세션 메모리에서 가져옴
        chat_history = request.session.get('chat_history', [])

    # 3. 템플릿으로 데이터 전달
    context = {
        'chat_history': chat_history,  # 이제 result 하나가 아니라 전체 기록을 보냅니다
        'error': error,
    }
    
    return render(request, 'medical_app/index.html', context)


def home(request):
    """랜딩 페이지"""
    return render(request, 'medical_app/home.html')