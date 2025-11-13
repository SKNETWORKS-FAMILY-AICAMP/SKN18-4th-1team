"""
증상 분석 서비스 로직
"""
from Feature_rag.langgraph_structure.graph import create_graph_flow

langgraph_app = create_graph_flow()

def analyze_symptoms(symptoms_text):
    # return {'diseases': diseases, 'hospitals': hospitals}
    #--> return이 반드시 이 딕셔너리 형식이여야 함
    """
    LangGraph를 실행하고 AI의 '텍스트 답변'을 반환합니다.
    """
    # 1. LangGraph 실행
    input_data = {"question": symptoms_text}
    response_state = langgraph_app.invoke(input_data)
    
    # 2. 최종 답변(문자열) 추출
    # generation_llm.py가 생성한 'final_answer' 키의 값을 가져옵니다.
    final_answer_text = response_state.get("final_answer", "죄송합니다. 답변을 생성할 수 없습니다.")
    
    return final_answer_text