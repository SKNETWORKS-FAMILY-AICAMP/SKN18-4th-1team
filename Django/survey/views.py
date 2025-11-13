# survey/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required # 로그인 필수
from .forms import SurveyForm
from .models import SurveyResponse

@login_required # 설문은 로그인한 사용자만 작성
def survey_view(request):
    try:
        # 이미 작성한 설문이 있는지 확인
        instance = SurveyResponse.objects.get(user=request.user)
    except SurveyResponse.DoesNotExist:
        instance = None

    if request.method == 'POST':
        # POST 요청: 폼 데이터 제출 시 (instance=instance로 기존 정보 업데이트)
        form = SurveyForm(request.POST, instance=instance)
        if form.is_valid():
            # 폼이 유효하면 저장
            survey = form.save(commit=False) # 아직 DB에 저장 X
            survey.user = request.user # 현재 로그인한 사용자를 설문과 연결
            survey.save() # DB에 저장
            
            # 설문 완료 후 챗봇 메인 페이지 등으로 이동
            return redirect('chatbot_main') # 'chatbot_main'은 예시 URL 이름
    else:
        # GET 요청: 폼 페이지를 처음 열 때 (instance=instance로 기존 정보 불러오기)
        form = SurveyForm(instance=instance)

    return render(request, 'survey/survey_form.html', {'form': form})