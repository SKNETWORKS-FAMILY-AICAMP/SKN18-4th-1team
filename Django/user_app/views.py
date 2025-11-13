from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import (
    CustomUserChangeForm,
    CustomUserCreationForm,
    EmailOrUsernameAuthenticationForm,
)
from .models import ChatSession


def login_view(request):
    """Render and process the local login form at /users/."""
    if request.user.is_authenticated:
        return redirect('medical_app:index')

    form = EmailOrUsernameAuthenticationForm(request=request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('medical_app:index')

    return render(request, 'user_app/login.html', {'form': form})


def signup_view(request):
    """
    Displays the custom signup form for users who prefer email/password signup.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('medical_app:index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'user_app/signup.html', {'form': form})


@login_required
def mypage_view(request):
    """
    Shows profile info and accumulated chat history for the authenticated user.
    """
    chat_sessions = (
        ChatSession.objects.filter(user=request.user)
        .prefetch_related('messages')
        .order_by('-created_at')
    )
    return render(
        request,
        'user_app/profile.html',
        {
            'user': request.user,
            'chat_sessions': chat_sessions,
        },
    )


@login_required
def logout_view(request):
    """
    Handle logout confirmation and POST-based sign-out for CSRF protection.
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, '로그아웃되었습니다.')
        return redirect('medical_app:home')

    return render(request, 'user_app/logout.html')


@login_required
def profile_edit_view(request):
    """
    Simple profile edit form.
    """
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 수정되었습니다.')
            return redirect('accounts:account_profile')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'user_app/profile_edit.html', {'form': form})
