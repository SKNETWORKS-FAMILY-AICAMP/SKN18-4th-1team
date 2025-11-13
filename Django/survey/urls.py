# survey/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 'survey/' URL로 접속하면 survey_view 함수를 실행
    path('', views.survey_view, name='survey_form'), 
]