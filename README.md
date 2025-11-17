# 의료 RAG 시스템 (Medical RAG System)

LangGraph 기반의 의료 정보 검색 및 병원 추천 시스템입니다. 사용자의 증상을 분석하고, 관련 의료 정보를 제공하며, 적절한 병원을 추천합니다.

## 📋 목차

- [주요 기능](#주요-기능)
- [시스템 구조](#시스템-구조)
- [설치 방법](#설치-방법)
- [환경 설정](#환경-설정)
- [데이터베이스 설정](#데이터베이스-설정)
- [LangSmith를 사용한 테스트 및 모니터링](#-langsmith를-사용한-테스트-및-모니터링)
- [프로젝트 구조](#프로젝트-구조)
- [기술 스택](#기술-스택)
- [병원 추천 알고리즘](#-병원-추천-알고리즘)

## 🎯 주요 기능

1. **증상 분류 및 분석**
   - 사용자 질문을 의료 관련/비의료로 분류
   - 증상 기반 질문과 병원 추천 요청 구분
   - 진료과 자동 분류

2. **의료 정보 검색 (RAG)**
   - 질문을 의학적 키워드로 재작성
   - PostgreSQL + pgvector를 활용한 벡터 검색
   - 관련성 평가를 통한 문서 필터링
   - 웹 검색 fallback 지원

3. **증상 판단**
   - 의심 질환 추정
   - 중증도 판단 (HIGH/MID/LOW)
   - 최종 진료과 추천

4. **병원 추천**
   - 지역 기반 병원 검색
   - 중증도에 따른 가중치 적용
   - 간호등급, 의료인력, 장비 등 종합 평가

5. **대화 메모리 관리**
   - 대화 이력 요약 및 저장
   - 컨텍스트 유지

## 🏗️ 시스템 구조

```
┌─────────────┐
│ classify_node │ → 질문 분류 (증상/병원/무관)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ rewrite_question │ → 의학적 키워드로 재작성
└────────┬────────┘
         │
         ▼
┌─────────────┐
│ search_node │ → 벡터 DB 검색
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ evaluate_chunk   │ → 관련성 평가
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────────┐
│ symptom │ │   hospital   │
│  path   │ │    path      │
└────┬────┘ └──────┬───────┘
     │             │
     │      ┌──────▼──────┐
     │      │ judgment_   │
     │      │ symptom     │
     │      └──────┬──────┘
     │             │
     │      ┌──────▼──────┐
     │      │ search_     │
     │      │ hospital    │
     │      └──────┬──────┘
     │             │
     └──────┬──────┘
            ▼
    ┌───────────────┐
    │ generation_llm │ → 최종 답변 생성
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ memory_update │ → 대화 메모리 업데이트
    └───────────────┘
```

## 📦 설치 방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd SKN18-4th-1team
```

### 2. Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 의존성 패키지

주요 패키지:
- `langchain==1.0.3`
- `langchain-core==1.0.5`
- `langchain-openai==1.0.2`
- `langgraph==1.0.2`
- `psycopg2==2.9.11`
- `tavily-python==0.7.13`
- `pandas==2.3.3`

전체 목록은 `requirements.txt`를 참조하세요.

## ⚙️ 환경 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 환경 변수를 설정하세요:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# PostgreSQL 연결 정보
CONNECTION_STRING=postgresql://<user_id>:<password>@localhost:5432/<database>

# Tavily API (웹 검색용)
TAVILY_API_KEY=your_tavily_api_key

# LangSmith (모니터링 및 디버깅용, 선택사항)
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=your_langsmith_api_project_name
```

## 🗄️ 데이터베이스 설정

### Docker를 사용한 PostgreSQL + pgvector 설정

1. Docker Compose로 데이터베이스 실행:

```bash
cd Docker_medical
docker-compose up -d
```

2. 데이터베이스가 정상적으로 실행되었는지 확인:

```bash
docker ps
```

### 데이터베이스 스키마
- `medical_table`: 의료 지식 문서 및 임베딩 벡터 저장
- `hospital_table`: 병원 정보 저장


### 의료 문서 임베딩
의료 문서를 벡터 DB에 임베딩하려면:

```bash
cd mediscope
python ingest_doc.py
```

이 스크립트는 `Data/merged_with_domain.csv` 파일을 읽어 벡터 DB에 저장합니다.

## 🧪 LangSmith를 사용한 테스트 및 모니터링

LangSmith는 LangChain/LangGraph 애플리케이션의 실행 추적, 디버깅, 성능 모니터링을 제공하는 도구입니다.

### 1. LangSmith 계정 설정

1. [LangSmith](https://smith.langchain.com/)에 가입하고 로그인
2. Settings → API Keys에서 API 키 생성
3. `.env` 파일에 API 키 추가:
   ```env
   LANGCHAIN_API_KEY=ls-xxxxx
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=your_langsmith_api_project_name
   ```

### 2. 테스트 실행

환경 변수를 설정한 후 다음 명령어로 개발 서버를 실행합니다:

```bash
cd mediscope
uv pip install -e .
langgraph dev
```

이 명령어는:
- 로컬 서버에서 그래프를 실행합니다
- LangSmith와 자동으로 연동됩니다
- 웹 UI를 통해 대화형으로 테스트할 수 있습니다

#### 테스트 입력 예제

웹 UI에서 다음 예제 입력을 사용할 수 있습니다:

```json
{
  "question": "눈이 뻑뻑하고 침침해요.",
  "region": "서울특별시 도봉구",
  "survey_result": "사용자는 35세 여자이며, 임신 중이 아니며, BMI 정상, 기저질환 없음."
}
```

### 3. LangSmith 대시보드에서 확인

1. [LangSmith 대시보드](https://smith.langchain.com/) 접속
2. 설정한 프로젝트 이름 선택 (예: `your_langsmith_api_project_name`)
3. 실행 추적 확인:
   - 각 노드의 실행 시간
   - LLM 호출 및 응답
   - 상태 전환 과정
   - 에러 발생 지점
   - 입력/출력 데이터

### 4. 주요 기능

- **실행 추적**: 각 노드의 입력/출력 확인
- **성능 분석**: 노드별 실행 시간 측정
- **에러 디버깅**: 실패한 노드의 상세 정보 확인
- **비용 추적**: LLM API 호출 비용 모니터링
- **프롬프트 테스트**: 프롬프트 변경에 따른 결과 비교

### 5. 추적 비활성화

LangSmith 추적을 비활성화하려면 `.env` 파일에서 다음을 설정하거나 환경 변수를 제거하세요:

```env
LANGCHAIN_TRACING_V2=false
```

## 📁 프로젝트 구조

```
SKN18-4th-1team/
├── mediscope/                    # 메인 프로젝트 디렉토리
│   ├── langgraph_structure/      # LangGraph 구조
│   │   ├── graph.py              # 그래프 정의
│   │   ├── init_state.py         # 상태 정의
│   │   ├── utils.py              # 유틸리티 함수
│   │   ├── nodes/                # 노드 모듈
│   │   │   ├── classify_node.py      # 질문 분류
│   │   │   ├── rewrite_question.py   # 질문 재작성
│   │   │   ├── search_node.py        # 벡터 검색
│   │   │   ├── eval_node.py          # 관련성 평가
│   │   │   ├── judgment_symtom.py    # 증상 판단
│   │   │   ├── search_hospital.py    # 병원 검색
│   │   │   ├── generation_llm.py     # 답변 생성
│   │   │   ├── memory_node.py        # 메모리 업데이트
│   │   │   └── web_search.py         # 웹 검색
│   │   └── Rag/                  # RAG 관련 모듈
│   │       ├── custom_pgvector.py
│   │       ├── custom_ingest.py
│   │       └── custom_loader.py
│   ├── ingest_doc.py             # 문서 임베딩 스크립트
│   └── langgraph.json            # LangGraph 설정
├── Docker_medical/               # Docker 설정
│   ├── docker-compose.yml
│   └── init.sql                  # DB 초기화 스크립트
├── Data/                         # 데이터 파일
│   ├── merged_with_domain.csv    # 의료 문서 데이터
│   └── hospital_full_info_with_department.csv
├── main.py                       # 메인 진입점
├── requirements.txt              # Python 패키지 목록
└── README.md                     # 이 파일
```

## 🛠️ 기술 스택

- **프레임워크**: LangGraph, LangChain, RAG
- **LLM**: OpenAI GPT (gpt-5-nano)
- **벡터 DB**: PostgreSQL + pgvector
- **임베딩**: OpenAI text-embedding-3-small
- **웹 검색**: Tavily API
- **모니터링**: LangSmith
- **언어**: Python

## 📝 주요 노드 설명

### classify_node
- 사용자 질문을 `symptom`, `hospital`, `irrelevant`로 분류
- 진료과 자동 분류

### rewrite_question
- 일상 표현을 의학적 키워드로 변환
- 검색 최적화를 위한 질문 재작성

### search_node
- pgvector를 활용한 유사도 검색
- 진료과 필터링 지원

### evaluate_chunk
- 검색된 문서의 관련성 평가 (0-100점)
- 점수 50 이상만 필터링

### judgment_symtom
- 의심 질환 추정
- 중증도 판단 (HIGH/MID/LOW)
- 최종 진료과 결정

### search_hospital
- 지역 기반 병원 검색
- 중증도별 가중치 적용
- 간호등급, 의료인력, 장비 종합 평가

### generation_llm
- 증상 안내 또는 병원 추천 답변 생성
- 참고 문서 출처 포함

### memory_node
- 대화 이력 요약 및 저장
- 컨텍스트 유지

## 🏥 병원 추천 알고리즘

병원 추천은 증상 분석 결과와 사용자 지역 정보를 기반으로 최적의 병원을 추천합니다.

### 1. 증상 분석 단계 (judgment_symtom_node)

사용자의 증상, 설문 정보, 검색된 의료 문서를 종합하여 다음을 판단합니다:

- **의심 질환**: 증상과 가장 일치하는 질환 1개 선택
- **중증도**: `HIGH` / `MID` / `LOW` 중 하나 판단
- **최종 진료과**: 필요한 진료과 리스트 결정

### 2. 병원 검색 단계 (search_hospital_node)

#### 2.1 지역 기반 검색 (Fallback 방식)

사용자 주소를 파싱하여 좁은 범위부터 넓은 범위로 순차적으로 검색합니다:

```
도로명 → 동/읍/면 → 구 → 시/군 → 시/도
```

예시: "서울특별시 강남구 청담동" 입력 시
1. Level 0: "청담동" 포함 병원 검색
2. Level 1: "강남구" 포함 병원 검색 (Level 0 결과 없을 시)
3. Level 2: "서울특별시" 포함 병원 검색 (Level 1 결과 없을 시)

#### 2.2 진료과 필터링

검색된 병원 중에서 `judgment_symtom_node`에서 결정된 진료과를 보유한 병원만 선별합니다.

#### 2.3 점수 계산

각 병원에 대해 두 가지 점수를 계산합니다:

**의료역량 점수 (Care Score)**
- 평가 기준 (6개):
  - 간호인력
  - 의료인력
  - 건강보험
  - 건강보험(환자수)
  - 의료급여
  - 의료급여(환자수)

- 간호등급 변환: 1등급(105점) ~ 7등급(15점)

- 중증도별 의료역량 세부 가중치:
  - `HIGH`: 간호인력 30%, 의료인력 40%, 건강보험(환자수) 15%, 기타 15%
  - `MID`: 간호인력 35%, 의료인력 25%, 건강보험 15%, 기타 25%
  - `LOW`: 간호인력 20%, 의료인력 10%, 건강보험 20%, 기타 50%

**거리 점수 (Distance Score)**
- 검색 레벨에 따라 점수 부여:
  - Level 0 (도로명/동): 100점
  - Level 1 (구): 80점
  - Level 2 (시/군): 60점
  - Level 3 (시/도): 40점
  - Level 4 (기타): 20점

#### 2.4 최종 점수 계산

의료역량 점수와 거리 점수를 중증도에 따라 가중 평균하여 최종 점수를 계산합니다:

```
최종 점수 = (의료역량 점수 × 의료역량 가중치) + (거리 점수 × 거리 가중치)
```

**중증도별 의료역량과 거리 가중치:**
- **HIGH** (중증): 의료역량 80%, 거리 20%
  - 심각한 증상이므로 의료 역량이 우선
- **MID** (중등도): 의료역량 50%, 거리 50%
  - 의료 역량과 접근성 균형 고려
- **LOW** (경증): 의료역량 20%, 거리 80%
  - 가까운 병원이 우선

### 3. 최종 추천 및 답변 생성

1. **병원 정렬**: 최종 점수가 높은 순서로 정렬
2. **상위 3개 선정**: 점수 상위 3개 병원 추천
3. **답변 생성** (`generation_llm_node`):
   - 추천 이유 및 진료과 적합성 설명
   - 간호등급, 의료인력, 장비 등 구체적 근거 제시
   - 참고 문서 출처 표시

### 예시

```
입력:
- 질문: "귀에서 삐— 소리가 계속 들려요"
- 지역: "서울특별시 강남구 청담동"
- 설문: "40세 여자, BMI 정상, 기저질환 없음"

처리 과정:
1. 증상 분석 → 의심 질환: "이명", 중증도: "MID", 진료과: ["이비인후과"]
2. 지역 검색 → "청담동" → "강남구" → "서울특별시" 순으로 검색
3. 이비인후과 필터링
4. 점수 계산 (MID: 의료역량 50%, 거리 50%)
5. 상위 3개 병원 추천 및 답변 생성
```

## ⚠️ 주의사항

1. **의료 정보 제공 한계**: 이 시스템은 정보 제공 목적이며, 실제 진단이나 치료를 대체할 수 없습니다.
2. **API 키 보안**: `.env` 파일은 절대 버전 관리에 포함하지 마세요.
3. **데이터베이스**: PostgreSQL이 실행 중이어야 합니다.


## 🔧 문제 해결

### Import 오류
```bash
pip install -r requirements.txt
```

### 데이터베이스 연결 오류
- Docker 컨테이너가 실행 중인지 확인
- `.env` 파일의 `CONNECTION_STRING` 확인

### 벡터 검색 결과 없음
- `ingest_doc.py`를 실행하여 문서를 임베딩했는지 확인