from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def rewrite_question_node():
    """
    RAG 검색 성능을 높이기 위해 질문을 다시 작성하는 프롬프트 정의
    """
    template = """
    당신은 RAG 시스템의 질문 개선 전문가입니다.
    아래 질문을 벡터 검색에서 더 잘 검색되도록 구체적이고 명확하게 다시 작성하세요.

    원래 질문: {question}

    조건:
    1. 질문은 반드시 하나의 완전한 문장으로 작성하세요.
    2. 불필요한 감정 표현, 문장 부호, 조사 등을 제거하세요.
    3. 가능한 한 구체적인 단어나 개념을 사용하세요.
    4. 오직 재작성된 질문 한 문장만 출력하세요.
    """
    return ChatPromptTemplate.from_template(template)


def rewrite_question(state: dict) -> dict:
    """
    eval 단계 이후, 질문을 RAG 검색에 더 적합하게 다시 작성하는 노드
    """
    model = ChatOpenAI(
        model="gpt-5-nano",
        reasoning_effort="low"
    )

    chain = rewrite_question_node() | model

    # 실제 질문 사용
    question = state.get("question", "")

    # 모델 실행
    response = chain.invoke({
        "question": question
    })

    # 결과 추출
    rewritten_question = getattr(response, "content", str(response)).strip()

    return {
        **state,
        "question": rewritten_question,
        "route": "classify"
    }
