# 질문이 rag에 적합한 질문이도록 다시 질문을 작성하는 node
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.prompts import PromptTemplate
from langgraph import Node, Graph
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

    원래 질문: {retrieval_question}

    조건:
    1. 질문은 반드시 하나의 완전한 문장으로 작성하세요.
    2. 불필요한 감정 표현, 문장 부호, 조사 등을 제거하세요.
    3. 가능한 한 구체적인 단어나 개념을 사용하세요.
    4. 오직 재작성된 질문 한 문장만 출력하세요.
    """

    return PromptTemplate.from_template(template)


def rewrite_question(state: dict) -> dict:
    """
    eval 단계 이후, 질문을 RAG 검색에 더 적합하게 다시 작성하는 노드
    """

    model = ChatOpenAI(
        model="gpt-5-nano",
        reasoning_effort="low"
    )

    chain = rewrite_question_node() | model

    # GraphState(혹은 state dict)에서 원본 질문 추출
    retrieval_question = state.get("retrieval_question", "")

    # 모델 실행
    response = chain.invoke({
        "retrieval_question": retrieval_question
    })

    question = response.content.strip()

    # 수정된 질문을 상태에 저장 후 반환
    return {
        **state,
        "rewritten_question": question,
        "route": "classify"   # 다음 단계로 라우팅 예시
    }