# survey/models.py
from django.db import models
from django.conf import settings 
# settings.AUTH_USER_MODEL을 사용하면 user_app의 User 모델을 
# 직접 가져오지 않고도 안전하게 참조할 수 있습니다.

class SurveyResponse(models.Model):
    # 성별 선택지
    class GenderChoices(models.TextChoices):
        MALE = 'M', '남성'
        FEMALE = 'F', '여성'
        OTHER = 'O', '기타'

    # 사용자 모델과 1:1 연결
    # related_name='survey'를 통해 user.survey로 이 모델에 접근 가능
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='survey'
    )
    
    # 나이
    age = models.PositiveIntegerField()
    
    # 성별
    gender = models.CharField(
        max_length=1,
        choices=GenderChoices.choices
    )
    
    # 임신 여부 (기본값 False)
    is_pregnant = models.BooleanField(default=False)
    
    # 지병 여부 (간단한 텍스트 입력)
    # blank=True, null=True: 선택 사항(없을 수도 있음)
    preexisting_conditions = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="지병"
    )

    address = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="주소"
    )

    def __str__(self):
        return f"{self.user.username}의 설문"