from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from survey.forms import SurveyForm
from survey.models import SurveyResponse
from survey.services import calculate_bmi

from .forms import (
    CustomUserChangeForm,
    CustomUserCreationForm,
    EmailOrUsernameAuthenticationForm,
)
from .models import ChatSession


def login_view(request):
    """Render and process the local login form at /users/."""
    redirect_to = request.POST.get('next') or request.GET.get('next')
    if request.user.is_authenticated:
        if redirect_to and url_has_allowed_host_and_scheme(
            redirect_to,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(redirect_to)
        return redirect('medical_app:index')

    form = EmailOrUsernameAuthenticationForm(request=request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        if redirect_to and url_has_allowed_host_and_scheme(
            redirect_to,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(redirect_to)
        return redirect('medical_app:index')

    return render(
        request,
        'user_app/login.html',
        {
            'form': form,
            'next': redirect_to,
        },
    )


def signup_view(request):
    """
    Displays the custom signup form for users who prefer email/password signup.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['show_survey_once'] = True
            return redirect('survey:survey_form')
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
    survey = getattr(request.user, 'survey', None)
    return render(
        request,
        'user_app/profile.html',
        {
            'user': request.user,
            'survey': survey,
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
    try:
        survey_instance = request.user.survey
    except SurveyResponse.DoesNotExist:
        survey_instance = None

    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        survey_form = SurveyForm(request.POST, instance=survey_instance)
        if user_form.is_valid() and survey_form.is_valid():
            user_form.save()
            survey = survey_form.save(commit=False)
            survey.user = request.user
            bmi_value, bmi_category = calculate_bmi(
                survey.height_cm,
                survey.weight_kg,
            )
            survey.bmi = bmi_value
            survey.bmi_category = bmi_category
            survey.save()
            messages.success(request, '프로필이 수정되었습니다.')
            return redirect('accounts:account_profile')
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        survey_form = SurveyForm(instance=survey_instance)

    return render(
        request,
        'user_app/profile_edit.html',
        {
            'user_form': user_form,
            'survey_form': survey_form,
        },
    )
