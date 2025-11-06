from langchain_core.prompts import PromptTemplate
from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import model

def __get_prompt_for_rewriting_question():
    template = """
    # **질문 재작성 작업**

    당신은 **RAG 검색 품질 개선 전문가**입니다.
    사용자의 질문을 벡터DB 검색에 최적화된 문장으로 **한국어로 재작성**하세요.

    ## 참고 자료
    아래는 이전 단계에서 평가된 메시지입니다.
    이를 참고하여 더 명확하고 구체적인 질문으로 바꿔주세요.

    ---
    # 평가 메세지:
    {feedback_messages}

    # 원본 질문:
    {question}

    ---
    # 출력 형식
    - 오직 하나의 재작성된 문장만 출력합니다.
    - 설명이나 추가 문구 없이 질문만 작성합니다.
    """

    return PromptTemplate.from_template(template)

def question_retrive(state: GraphState) -> GraphState:
    """Rewrite the question for a better retrieval query."""

    llm = model("gpt-5-nano",temperature=0.3)
    chain = __get_prompt_for_rewriting_question() | llm
    
    result = chain.invoke({
        "question": state["question"],
        "feedback_messages":state["feedback_messages"],
    })
    return {
        **state,
        "question": result.content,
        "max_token": True,
    }
