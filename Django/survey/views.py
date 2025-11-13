# survey/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SurveyForm
from .models import SurveyResponse

@login_required
def survey_view(request):
    show_after_signup = request.session.pop('show_survey_once', False)

    try:
        instance = SurveyResponse.objects.get(user=request.user)
    except SurveyResponse.DoesNotExist:
        instance = None

    if not show_after_signup and instance is None:
        return redirect('medical_app:home')

    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=instance)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.user = request.user
            survey.save()
            return redirect('chatbot_main')
    else:
        form = SurveyForm(instance=instance)

    return render(request, 'survey/survey_form.html', {'form': form})
