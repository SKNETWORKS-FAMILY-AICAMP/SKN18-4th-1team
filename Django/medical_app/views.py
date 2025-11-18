import json
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from user_app.models import ChatMessage, ChatSession
from survey.models import SurveyResponse
from .services import analyze_symptoms


logger = logging.getLogger("medical_app")


def _get_or_create_session_for_user(request, *, create=True):
    """
    인증된 사용자를 위한 ChatSession을 가져온다.
    create=False인 경우에는 존재하지 않으면 None을 반환한다.
    """
    if not request.session.session_key:
        request.session.save()
        logger.info("[chat] generated new session_key=%s", request.session.session_key)

    chat_session = ChatSession.objects.filter(
        session_key=request.session.session_key
    ).first()

    if chat_session is None and create:
        chat_session = ChatSession.objects.create(
            session_key=request.session.session_key,
            user=request.user if request.user.is_authenticated else None,
        )
        logger.info("[chat] created ChatSession id=%s key=%s user=%s", chat_session.id, chat_session.session_key, chat_session.user_id)

    if chat_session and chat_session.user_id is None and request.user.is_authenticated:
        chat_session.user = request.user
        chat_session.save(update_fields=['user'])

    return chat_session


def _ensure_region_from_survey(request):
    if request.session.get('chat_region'):
        return request.session['chat_region']
    if not request.user.is_authenticated:
        return None
    try:
        survey = request.user.survey
    except AttributeError:
        return None
    except SurveyResponse.DoesNotExist:
        return None
    if survey.address:
        request.session['chat_region'] = survey.address
        request.session.modified = True
        return survey.address
    return None


def _build_survey_summary(request):
    cached = request.session.get('chat_survey_summary')
    if cached:
        return cached

    if not request.user.is_authenticated:
        return None

    try:
        survey = request.user.survey
    except AttributeError:
        return None
    except SurveyResponse.DoesNotExist:
        return None

    gender = (
        "남성"
        if survey.gender == SurveyResponse.GenderChoices.MALE
        else "여성"
    )
    pregnancy = "임신 중" if survey.pregnancy else "임신 중이 아님"
    conditions = survey.preexisting_conditions or "기저질환 없음"
    bmi_section = ""
    if survey.bmi and survey.bmi_category:
        bmi_section = f"BMI는 {survey.bmi} ({survey.get_bmi_category_display()})"
    summary = (
        f"사용자는 {survey.age}세 {gender}이며, {pregnancy} 상태입니다. "
        f"{bmi_section} "
        f"기저질환: {conditions}."
    ).strip()

    request.session['chat_survey_summary'] = summary
    if survey.address and not request.session.get('chat_region'):
        request.session['chat_region'] = survey.address
    request.session.modified = True
    return summary


def _store_message(request, role, content):
    """
    모든 사용자의 채팅 메시지를 세션에만 적재합니다.
    """
    history = request.session.get('chat_history', [])
    history.append({'role': role, 'content': content})
    request.session['chat_history'] = history
    request.session.modified = True
    logger.info("[chat] store_message role=%s, history_len=%s, session_key=%s", role, len(history), request.session.session_key)


def _store_summary_entry(request, summary_text: str):
    """
    LangGraph에서 만들어준 요약만 ChatMessage DB에 저장합니다.
    """
    if not summary_text:
        logger.info("[chat] summary empty, skip DB persist.")
        return

    chat_session = _get_or_create_session_for_user(request)
    if chat_session is None:
        logger.warning("[chat] cannot persist summary: chat_session missing.")
        return

    logger.info(
        "[chat] storing summary (len=%s) for session %s",
        len(summary_text),
        chat_session.id or "anonymous",
    )
    ChatMessage.objects.update_or_create(
        session=chat_session,
        role=ChatMessage.Role.SYSTEM,
        defaults={'content': summary_text},
    )
    chat_session.save(update_fields=['updated_at'])
    request.session['chat_memory_summary'] = summary_text
    request.session.modified = True


def index(request):
    """
    메인 뷰: 채팅 기록을 불러오고, 새로운 질문을 처리합니다.
    """
    error = None
    
    # 세션에 요약이 없다면 DB에서 복원
    _hydrate_summary_from_db(request)

    # 1. POST 요청 처리 (사용자가 질문을 보냈을 때)
    if request.method == 'POST':
        symptoms = request.POST.get('symptoms', '').strip()
        
        if not symptoms:
            error = '내용을 입력해주세요.'
        else:
            try:
                awaiting_region = request.session.get('awaiting_region', False)
                if awaiting_region:
                    logger.info("[chat] received region input while awaiting location.")
                    _store_message(request, ChatMessage.Role.USER, symptoms)
                    request.session['chat_region'] = symptoms
                    request.session['awaiting_region'] = False
                    request.session.modified = True
                    question_for_ai = request.session.pop('pending_hospital_question', symptoms)
                else:
                    logger.info("[chat] POST question='%s'", symptoms)
                    _store_message(request, ChatMessage.Role.USER, symptoms)
                    question_for_ai = symptoms

                memory_summary = request.session.get('chat_memory_summary')
                if not memory_summary:
                    memory_summary = _hydrate_summary_from_db(request)
                survey_summary = _build_survey_summary(request)
                region_value = request.session.get('chat_region') or _ensure_region_from_survey(request)

                logger.info(
                    "[chat] memory_summary len=%s, region=%s",
                    len(memory_summary) if memory_summary else 0,
                    region_value,
                )

                response_state = analyze_symptoms(
                    question_for_ai,
                    memory_summary=memory_summary,
                    region=region_value,
                    survey_summary=survey_summary,
                )
                ai_response = response_state.get("final_answer", "")
                logger.info("[chat] AI response len=%s", len(ai_response))

                # (3) AI 답변 저장
                _store_message(
                    request,
                    ChatMessage.Role.ASSISTANT,
                    ai_response
                )

                # (4) LangGraph가 반환한 요약을 세션에 저장하여 memory로 활용
                new_summary = response_state.get("summary")
                if new_summary and not response_state.get("need_region"):
                    _store_summary_entry(request, new_summary)
                if response_state.get("need_region"):
                    request.session['awaiting_region'] = True
                    request.session['pending_hospital_question'] = question_for_ai
                    request.session.modified = True
            except Exception:
                logger.exception("[chat] analyze_symptoms failed")
                error = '오류가 발생했습니다. 잠시 후 다시 시도해주세요.'

    # 2. 대화 기록 불러오기 (GET, POST 모두 실행)
    chat_history = request.session.get('chat_history', [])
    active_session = _get_or_create_session_for_user(request, create=False)

    # 3. 템플릿으로 데이터 전달
    context = {
        'chat_history': chat_history,  # 이제 result 하나가 아니라 전체 기록을 보냅니다
        'error': error,
        'active_session': active_session,
    }
    
    return render(request, 'medical_app/index.html', context)


def home(request):
    """랜딩 페이지"""
    return render(request, 'medical_app/home.html')


@login_required
@require_POST
def delete_active_chat(request):
    chat_session = _get_or_create_session_for_user(request, create=False)
    if chat_session and chat_session.user_id == request.user.id:
        ChatMessage.objects.filter(session=chat_session).delete()
        chat_session.delete()
    request.session.pop('chat_history', None)
    request.session.pop('chat_memory_summary', None)
    request.session.pop('chat_region', None)
    request.session.pop('chat_survey_summary', None)
    request.session.pop('awaiting_region', None)
    request.session.pop('pending_hospital_question', None)
    request.session.modified = True
    return redirect('medical_app:index')
def _hydrate_summary_from_db(request):
    """
    세션에 요약이 없고 DB에 저장된 상담 요약이 있다면 불러와서 세션에 복원합니다.
    현재 브라우저 세션 키에 해당하는 ChatSession만 대상으로 합니다.
    """
    cached = request.session.get('chat_memory_summary')
    if cached:
        logger.info("[chat] cached summary found len=%s for session_key=%s", len(cached), request.session.session_key)
        return cached

    if not request.session.session_key:
        request.session.save()

    chat_session = ChatSession.objects.filter(
        session_key=request.session.session_key
    ).first()
    if not chat_session:
        logger.info(
            "[chat] no chat_session found for key=%s",
            request.session.session_key,
        )
        return None

    summaries = list(
        ChatMessage.objects.filter(
            session=chat_session,
            role=ChatMessage.Role.SYSTEM,
        )
        .order_by('-id')
        .values_list('content', flat=True)[:1]
    )
    last_summary = summaries[0] if summaries else None
    if last_summary:
        logger.info(
            "[chat] hydrate summary (session_id=%s, key=%s, len=%s)",
            chat_session.id,
            chat_session.session_key,
            len(last_summary),
        )
        request.session['chat_memory_summary'] = last_summary
        request.session.modified = True
        return last_summary
    logger.info(
        "[chat] no summary rows for session_id=%s key=%s",
        chat_session.id,
        chat_session.session_key,
    )
    return None
