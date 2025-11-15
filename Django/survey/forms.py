# survey/forms.py
from django import forms
from .models import SurveyResponse

class SurveyForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        
        # [수정] fields 리스트에 'address' 추가
        fields = [
            'age',
            'height_cm',
            'weight_kg',
            'gender',
            'pregnancy',
            'preexisting_conditions',
            'address',
        ]
        
        # [수정] labels 에 'address' 한글 이름 추가
        labels = {
            'age': '나이',
            'height_cm': '키 (cm)',
            'weight_kg': '몸무게 (kg)',
            'gender': '성별',
            'pregnancy': '임신 여부',
            'preexisting_conditions': '지병 (있을 경우 기재)',
            'address': '주소 (선택)',
        }
        
        widgets = {
            'preexisting_conditions': forms.Textarea(attrs={'rows': 3}),
            # [선택] 주소 입력란도 크게 만들 수 있습니다.
            'address': forms.TextInput(attrs={'placeholder': '예: 서울시 강남구'}),
            'gender': forms.RadioSelect(),
            'height_cm': forms.NumberInput(),
            'weight_kg': forms.NumberInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].widget.attrs.update({
            'class': 'survey-input',
            'placeholder': '만 나이를 입력해주세요'
        })
        self.fields['height_cm'].widget.attrs.update({
            'class': 'survey-input',
            'placeholder': '예: 170',
            'min': 100,
            'max': 250
        })
        self.fields['weight_kg'].widget.attrs.update({
            'class': 'survey-input',
            'placeholder': '예: 65.5',
            'step': '0.1',
            'min': 10,
            'max': 250
        })
        self.fields['preexisting_conditions'].widget.attrs.update({
            'class': 'survey-textarea',
            'placeholder': '예: 당뇨, 고혈압, 천식 등'
        })
        self.fields['address'].widget.attrs.update({
            'class': 'survey-input',
            'placeholder': '예: 서울시 강남구'
        })
