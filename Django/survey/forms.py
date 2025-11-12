# survey/forms.py (새 파일)
from django import forms
from .models import SurveyResponse

class SurveyForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        # 폼에서 보여줄 필드 선택
        fields = ['age', 'gender', 'is_pregnant', 'preexisting_conditions']
        
        # 각 필드의 라벨(이름)을 한글로 변경
        labels = {
            'age': '나이',
            'gender': '성별',
            'is_pregnant': '임신 여부',
            'preexisting_conditions': '지병 (있을 경우 기재)',
        }
        
        # 위젯을 사용해 폼의 형태를 지정할 수 있습니다.
        # 예를 들어, 지병란을 더 크게 만듭니다.
        widgets = {
            'preexisting_conditions': forms.Textarea(attrs={'rows': 3}),
        }