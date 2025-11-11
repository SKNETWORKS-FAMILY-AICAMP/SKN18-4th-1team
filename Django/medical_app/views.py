from django.shortcuts import render
from .services import analyze_symptoms


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
                # 증상 분석 서비스 호출
                result = analyze_symptoms(symptoms)
            except Exception as e:
                error = f'분석 중 오류가 발생했습니다: {str(e)}'
    
    context = {
        'symptoms': symptoms,
        'result': result,
        'error': error,
    }
    
    return render(request, 'medical_app/index.html', context)

