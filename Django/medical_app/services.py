"""
증상 분석 서비스 로직
"""
from .models import Disease, DiseaseRecommendation, Hospital


def analyze_symptoms(symptoms_text):
    """
    증상을 분석하여 관련 질병과 병원을 반환합니다.
    """
    symptoms_lower = symptoms_text.lower()
    
    diseases = []
    hospitals = []
    
    # 키워드 기반 질병 매칭 (실제로는 LLM API를 호출할 수 있습니다)
    if any(keyword in symptoms_lower for keyword in ['두통', '머리', 'headache']):
        diseases = [
            {
                'name': '긴장성 두통',
                'description': '스트레스나 근육 긴장으로 인한 가장 흔한 형태의 두통입니다.',
                'severity': 'low',
                'recommendations': [
                    '충분한 휴식을 취하세요',
                    '스트레스 관리가 중요합니다',
                    '규칙적인 수면 패턴을 유지하세요'
                ]
            },
            {
                'name': '편두통',
                'description': '박동성 두통과 함께 메스꺼움, 빛 공포증이 동반될 수 있습니다.',
                'severity': 'medium',
                'recommendations': [
                    '조용하고 어두운 곳에서 휴식',
                    '트리거 음식 피하기',
                    '전문의 상담 권장'
                ]
            }
        ]
        hospitals = [
            {
                'name': '서울대학교병원 신경과',
                'specialty': '신경과',
                'distance': '1.2km',
                'waitTime': '약 30분',
                'address': '서울시 종로구 대학로 101',
                'phone': '02-2072-2114'
            },
            {
                'name': '세브란스병원 신경과',
                'specialty': '신경과',
                'distance': '2.5km',
                'waitTime': '약 45분',
                'address': '서울시 서대문구 연세로 50-1',
                'phone': '02-2228-5800'
            }
        ]
    elif any(keyword in symptoms_lower for keyword in ['기침', '콧물', '감기']):
        diseases = [
            {
                'name': '급성 상기도 감염 (감기)',
                'description': '바이러스에 의한 상기도 감염으로 콧물, 기침, 인후통 등이 나타납니다.',
                'severity': 'low',
                'recommendations': [
                    '충분한 수분 섭취',
                    '따뜻하게 휴식',
                    '증상이 1주일 이상 지속되면 병원 방문'
                ]
            }
        ]
        hospitals = [
            {
                'name': '강남세브란스병원 호흡기내과',
                'specialty': '호흡기내과',
                'distance': '0.8km',
                'waitTime': '약 20분',
                'address': '서울시 강남구 언주로 211',
                'phone': '02-2019-3114'
            },
            {
                'name': '삼성서울병원 호흡기내과',
                'specialty': '호흡기내과',
                'distance': '1.5km',
                'waitTime': '약 40분',
                'address': '서울시 강남구 일원로 81',
                'phone': '02-3410-2114'
            }
        ]
    elif any(keyword in symptoms_lower for keyword in ['복통', '배', '소화']):
        diseases = [
            {
                'name': '급성 위염',
                'description': '위 점막의 염증으로 복통, 소화불량, 메스꺼움 등이 나타납니다.',
                'severity': 'medium',
                'recommendations': [
                    '자극적인 음식 피하기',
                    '소량씩 자주 식사',
                    '심한 통증 시 즉시 병원 방문'
                ]
            },
            {
                'name': '과민성 대장 증후군',
                'description': '스트레스나 특정 음식에 의해 복통과 배변 습관 변화가 나타납니다.',
                'severity': 'low',
                'recommendations': [
                    '스트레스 관리',
                    '식이 조절',
                    '규칙적인 운동'
                ]
            }
        ]
        hospitals = [
            {
                'name': '서울아산병원 소화기내과',
                'specialty': '소화기내과',
                'distance': '1.1km',
                'waitTime': '약 35분',
                'address': '서울시 송파구 올림픽로 43길 88',
                'phone': '02-3010-3114'
            }
        ]
    else:
        diseases = [
            {
                'name': '일반적인 건강 상담 필요',
                'description': '입력하신 증상에 대한 정확한 진단을 위해 전문의 상담이 필요합니다.',
                'severity': 'medium',
                'recommendations': [
                    '가까운 병원을 방문하세요',
                    '증상의 시작 시기와 변화를 기록하세요',
                    '복용 중인 약이 있다면 의사에게 알려주세요'
                ]
            }
        ]
        hospitals = [
            {
                'name': '서울대학교병원 가정의학과',
                'specialty': '가정의학과',
                'distance': '1.2km',
                'waitTime': '약 25분',
                'address': '서울시 종로구 대학로 101',
                'phone': '02-2072-2114'
            }
        ]
    
    return {
        'diseases': diseases,
        'hospitals': hospitals
    }

