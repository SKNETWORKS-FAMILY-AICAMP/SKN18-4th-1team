#  뽑아져 나온 chunk를 평가하는 node
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from langgraph import Node, Graph
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def eval_node(inputs: dict) -> dict:
    """
    뽑아져 나온 chunk(검색 결과)를 평가하는 노드
    """
    # classify_node에서 전달된 질문
    question = inputs.get("question")

    # retriever 같은 노드에서 전달된 검색 결과
    chunks = inputs.get("search_results", [])

    # 상위 5개만 선택
    top_chunks = chunks[:5]

    # LLM에게 평가를 요청할 프롬프트 구성
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 의료 전문 어시스턴트야. 사용자의 질문과 관련성이 높은 문서를 판단해."),
        ("human", "질문: {question}\n검색 결과:\n{chunks}\n이 중 어떤 문서가 가장 유사도가 높은가")
    ])

    model = ChatOpenAI(
        model = 'gpt-5-nano',
        reasoning_effort ="low"
    )

    chain = chat_prompt | model

    # 평균 유사도 계산 (chunk에 score가 포함되어 있을 경우)
    if top_chunks and "score" in top_chunks[0]:
        avg_score = sum(c["score"] for c in top_chunks) / len(top_chunks)
        top_score = top_chunks[0]["score"]
    else:
        avg_score = 0
        top_score = 0

    # 기준 설정 (경험적으로 조정)
    # - 평균 점수 0.5 미만이거나
    # - 1위 점수가 0.65 미만이면 "관련성 낮음"
    if top_score < 0.65 or avg_score < 0.5:
        route = "rewrite_question"
    else:
        route = "generate_answer"

    return {
        "question": question,
        "chunks": top_chunks,
        "route": route
    }