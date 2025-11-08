from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate

def generation_llm_node():
    """
    최종 답변 생성용 PromptTemplate
    이전 단계에서 검색된 병원 정보와 질문을 바탕으로
    사용자에게 전달할 자연스러운 답변을 생성
    """
    template = """
    당신은 의료 안내 챗봇입니다.
    아래 정보를 참고하여 사용자에게 친절하고 이해하기 쉬운 답변을 작성하세요.

    [사용자 질문]
    {question}

    [검색된 병원 목록]
    {hospital_results}

    지침:
    1. 병원 이름을 명확히 표시하고, 어떤 이유로 추천했는지 간단히 설명하세요.
    2. 답변은 3~4문장으로 요약하고 자연스럽게 작성하세요.
    3. 의학적 진단이나 처방은 포함하지 마세요.

    출력:
    사용자가 바로 이해할 수 있는 자연스러운 한국어 문장
    """
    return PromptTemplate.from_template(template)


def generation_llm(state: dict) -> dict:
    """
    최종 답변 생성 노드
    - 입력: state dict에 이전 노드에서 가져온 'question'과 'hospital_results'
    - 출력: 최종 답변 'final_answer'를 포함하여 반환
    """
    # 모델 설정
    model = ChatOpenAI(model="gpt-5-nano", reasoning_effort="medium")

    # Prompt 템플릿 연결
    chain = generation_llm_node() | model

    # 이전 단계 결과 가져오기
    question = state.get("question", "")
    hospital_results = state.get("hospital_results", "")

    # LLM 실행
    response = chain.invoke({
        "question": question,
        "hospital_results": hospital_results
    })

    # 최종 답변 정리
    final_answer = response.content.strip()

    # 결과 반환 (워크플로우에서 다음 노드로 사용)
    return {
        **state,
        "final_answer": final_answer,  # 사용자에게 보여줄 최종 문장
        "route": "end"                 # 워크플로우 종료 시그널
    }
