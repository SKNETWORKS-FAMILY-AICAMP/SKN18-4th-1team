# survey/urls.py
from django.urls import path
from . import views

app_name = 'survey'

urlpatterns = [
    # 'survey/' URL에 접근하면 survey_view 함수가 실행
    path('', views.survey_view, name='survey_form'),
]
