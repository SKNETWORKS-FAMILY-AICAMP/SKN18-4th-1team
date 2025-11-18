from django.urls import path
from . import views

app_name = 'medical_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('consult/', views.index, name='index'),
    path('consult/delete', views.delete_active_chat, name='delete_chat'),
]

