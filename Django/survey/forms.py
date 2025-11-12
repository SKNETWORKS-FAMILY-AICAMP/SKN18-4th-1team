# survey/forms.py
from django import forms
from .models import SurveyResponse

class SurveyForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        
        # [수정] fields 리스트에 'address' 추가
        fields = ['age', 'gender', 'is_pregnant', 'preexisting_conditions', 'address']
        
        # [수정] labels 에 'address' 한글 이름 추가
        labels = {
            'age': '나이',
            'gender': '성별',
            'is_pregnant': '임신 여부',
            'preexisting_conditions': '지병 (있을 경우 기재)',
            'address': '주소 (선택)',
        }
        
        widgets = {
            'preexisting_conditions': forms.Textarea(attrs={'rows': 3}),
            # [선택] 주소 입력란도 크게 만들 수 있습니다.
            'address': forms.TextInput(attrs={'placeholder': '예: 서울시 강남구'}), 
        }