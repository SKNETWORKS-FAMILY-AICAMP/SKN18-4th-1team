# 증상을 의미하는 질문인지, 쓸데없는 질문인지 판별하는 node
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from langgraph import Node, Graph
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def classify_node(input_text: str) -> dict:
    """
    사용자의 질문이 증상과 관련된 질문인지 구분
    """
    chat_prompt = ChatPromptTemplate(
        messages=[
            # system 역할
            SystemMessage(
                content=("""
                    당신은 의료전문가 입니다.
                    사용자가 입력한 질문이 병원증상과 관련된 질문인지 판단합니다.
                    증상과 관련이 없는 질문이라면 "증상과 관련된 질문을 다시 입력해 주세요" 라고 대답합니다."""
                )
            ),
            # human 역할
            HumanMessagePromptTemplate.from_template("""
                {user_input}
            """),
        ]
    )
    model = ChatOpenAI(
        model = 'gpt-5-nano',
        reasoning_effort ="low"
    )

    # 체인 실행
    chain = chat_prompt | model
    response = chain.invoke({"user_input": input_text})
    answer = response.content.strip()

    # 결과 분기
    if "증상과 관련된 질문을 다시 입력해 주세요" in answer:
        route = "nonsymptom"
    else:
        route = "symptom"

    return {
        "question": input_text,
        "route": route,
        "answer": answer
    }


