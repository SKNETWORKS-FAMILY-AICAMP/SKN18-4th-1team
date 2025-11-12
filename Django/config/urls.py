"""
URL configuration for llmdesine_project project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('medical_app.urls')),
    path('accounts/', include('allauth.urls')),
    path('users/', include('user_app.urls')),
    path('survey/', include('survey.urls')),
    path('medical/', include('medical_app.urls')),
    path('user/', include('user_app.urls')),
]

