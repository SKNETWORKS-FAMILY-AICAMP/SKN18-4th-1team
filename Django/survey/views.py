# survey/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import SurveyForm
from .models import SurveyResponse
from .services import calculate_bmi


@login_required
def survey_view(request):
    show_after_signup = request.session.get('show_survey_once', False)

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
            bmi_value, bmi_category = calculate_bmi(
                survey.height_cm,
                survey.weight_kg,
            )
            survey.bmi = bmi_value
            survey.bmi_category = bmi_category
            survey.save()
            request.session.pop('show_survey_once', None)
            return redirect('medical_app:home')
    else:
        form = SurveyForm(instance=instance)

    return render(request, 'survey/survey_form.html', {'form': form})


@login_required
def skip_survey(request):
    if request.method == 'POST':
        request.session.pop('show_survey_once', None)
        return redirect('medical_app:home')
    return redirect('survey:survey_form')
