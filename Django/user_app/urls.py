from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 로그인 URL
    path('', views.login_view, name='login'),
    # 회원가입 URL
    path('signup/', views.signup_view, name='signup'),
    # 로그아웃 URL
    path('logout/', views.logout_view, name='logout'),
    # 마이페이지 URL
    path('profile/', views.mypage_view, name='account_profile'),
    # 프로필 수정 URL
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
] 
