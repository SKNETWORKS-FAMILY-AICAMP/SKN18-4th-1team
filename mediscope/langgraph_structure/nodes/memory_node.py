from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import model
from langchain_core.prompts import PromptTemplate

def memory_update_node(state: GraphState) -> GraphState:
    
    llm = model(model_name='gpt-5-nano', temperature=0.1, max_tokens=1024)
    template = """
    아래는 이전 요약입니다:
    {prev_summary}

    그리고 아래는 추가된 대화 내용입니다:
    - 사용자 질문: {question}
    - AI 답변: {final_answer} 

    위 두 내용을 바탕으로,
    핵심 정보만 남긴 간결한 요약을 만들어주세요.
    감정 표현, 군더더기 문장 없이 '사실 기반'으로 요약해주세요.
    """

    prompt = PromptTemplate.from_template(template)

    # 순서 중요: PromptTemplate | LLM
    chain = prompt | llm  
    
    result = chain.invoke({"prev_summary": state.get("summary", ""),
                        "question": state.get("question"),
                        "final_answer":state.get("final_answer")})
    
    state['summary'] = result.content
    
    return state