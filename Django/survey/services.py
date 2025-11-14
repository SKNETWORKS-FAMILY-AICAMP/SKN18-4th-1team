from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .models import SurveyResponse


def calculate_bmi(height_cm, weight_kg):
    """
    키(cm)와 몸무게(kg)를 이용해 BMI 값과 분류 결과를 반환한다.
    둘 중 하나라도 없거나 유효하지 않으면 (None, None)을 리턴한다.
    """
    if not height_cm or not weight_kg:
        return None, None

    try:
        height_m = Decimal(height_cm) / Decimal('100')
        weight = Decimal(weight_kg)
    except (InvalidOperation, TypeError):
        return None, None

    if height_m <= 0 or weight <= 0:
        return None, None

    bmi_value = (weight / (height_m * height_m)).quantize(
        Decimal('0.1'),
        rounding=ROUND_HALF_UP,
    )

    if bmi_value < Decimal('18.5'):
        category = SurveyResponse.BMICategory.UNDERWEIGHT
    elif bmi_value < Decimal('23'):
        category = SurveyResponse.BMICategory.NORMAL
    elif bmi_value < Decimal('25'):
        category = SurveyResponse.BMICategory.OVERWEIGHT
    else:
        category = SurveyResponse.BMICategory.OBESE

    return bmi_value, category
