# 질문이 rag에 적합한 질문이도록 다시 질문을 작성하는 node
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from langgraph import Node, Graph
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def rewrite_question_node(inputs: dict) -> dict:
    """
    질문이 RAG에 적합한 질문이도록 다시 질문을 작성하는 노드
    """
    question = inputs.get("question")

    # LLM에게 질문 재작성 요청
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 의료 전문 어시스턴트야. 사용자의 질문을 RAG에 적합하도록 재작성해."),
        ("human", "질문: {question}")
    ])

    model = ChatOpenAI(
        model = 'gpt-5-nano',
        reasoning_effort ="low"
    )

    chain = chat_prompt | model
    # LLM 실행
    rewritten = chain.invoke({"question": question}).content.strip()

    # 다음 노드로 분기 (다시 classify로)
    return {
        "question": rewritten,   # 재작성된 질문
        "route": "classify"      # 다음 단계로 라우팅
    }
    
