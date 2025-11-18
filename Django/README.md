# AI 의료 상담 시스템 (Django)

React/TypeScript로 만들어진 AI 의료 상담 시스템을 Django로 포팅한 버전입니다.

## 기능

- 증상 입력 및 분석 (순수 Django 서버 사이드 렌더링)
- 가능한 질병 추천
- 추천 병원 정보 제공
- 한국어 UI 지원
- JavaScript 없이 Django 템플릿만 사용

## 설치 방법

1. Python 가상환경 생성 및 활성화:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

3. 데이터베이스 마이그레이션:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. 개발 서버 실행:
```bash
python manage.py runserver
```

5. 브라우저에서 접속:
```
http://127.0.0.1:8000/
```

## 프로젝트 구조

```
llmdesine_django/
├── llmdesine_project/     # Django 프로젝트 설정
│   ├── settings.py        # 프로젝트 설정
│   ├── urls.py            # 메인 URL 설정
│   └── wsgi.py            # WSGI 설정
├── medical_app/           # 메인 앱
│   ├── models.py          # 데이터 모델
│   ├── views.py           # 뷰 함수
│   ├── urls.py            # URL 라우팅
│   ├── services.py        # 비즈니스 로직
│   └── templates/         # HTML 템플릿
├── static/                # 정적 파일
│   └── css/               # CSS 파일 (JavaScript 사용 안 함)
├── manage.py              # Django 관리 스크립트
└── requirements.txt       # 패키지 목록
```

## 주요 기능

### 증상 분석
- 사용자가 입력한 증상을 분석하여 관련 질병을 추천합니다.
- 키워드 기반 매칭을 사용합니다 (실제 LLM API 연동 가능).

### 질병 정보
- 각 질병에 대한 설명과 중증도 정보를 제공합니다.
- 질병별 권장사항을 표시합니다.

### 병원 추천
- 질병에 맞는 전문 병원을 추천합니다.
- 병원 정보 (주소, 전화번호, 거리, 대기시간)를 제공합니다.

## 개발 참고사항

### LLM API 연동
현재는 키워드 기반 매칭을 사용하고 있습니다. 실제 LLM API를 연동하려면 `medical_app/services.py`의 `analyze_symptoms` 함수를 수정하세요.

### 데이터베이스
SQLite를 기본 데이터베이스로 사용합니다. 프로덕션 환경에서는 PostgreSQL이나 MySQL을 사용하는 것을 권장합니다.

### 정적 파일
정적 파일은 `static/` 디렉토리에 있습니다. 개발 환경에서는 Django가 자동으로 서빙합니다.
- CSS 파일만 사용 (JavaScript 없음)
- 모든 기능은 Django 서버 사이드 렌더링으로 처리
- 폼 제출 후 페이지가 새로고침되어 결과를 표시

## 라이선스

이 프로젝트는 참고용으로 제공됩니다.

