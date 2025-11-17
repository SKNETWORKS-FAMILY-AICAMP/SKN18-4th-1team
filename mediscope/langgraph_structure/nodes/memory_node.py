from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import model
from langchain_core.prompts import PromptTemplate

def memory_update_node(state: GraphState) -> GraphState:
    
    llm = model(model_name='gpt-5-nano')
    template = """
    아래는 지금까지의 상담 요약입니다:
    {prev_summary}

    신규 대화:
    - 사용자 질문: {question}
    - AI 답변: {final_answer}

    위 정보를 통합하여 아래 지침을 지키는 새 요약을 만드세요.

    [요약 지침]
    1. 최소 2문장 이상 작성하고, 첫 문장은 사용자가 겪는 증상·상황을 정리합니다.
    2. 두 번째 문장에는 AI가 전달한 조언/권장 행동(필요 진료과, 주의사항 등)을 포함합니다.
    3. 불필요한 감정 표현이나 "핵심 요" 같은 짧은 단어만 쓰지 말고, 구체적인 설명을 담으세요.
    4. 만약 이전 요약이 없다면 새로 작성하고, 있다면 자연스럽게 이어서 최신 상태를 반영합니다.
    5. 항목 번호나 불릿 대신 일반 문장으로 작성합니다.
    """

    prompt = PromptTemplate.from_template(template)

    # 순서 중요: PromptTemplate | LLM
    chain = prompt | llm  
    
    result = chain.invoke({"prev_summary": state.get("summary", ""),
                        "question": state.get("question"),
                        "final_answer":state.get("final_answer")})
    
    state['summary'] = result.content
    
    return state
