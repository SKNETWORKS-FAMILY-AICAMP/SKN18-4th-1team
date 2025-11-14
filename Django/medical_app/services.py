"""
증상 분석 서비스 로직
"""
# ▼▼▼ [중요] 에러가 나는 RAG 관련 임포트를 모두 주석 처리합니다 ▼▼▼
# from Feature_rag.langgraph_structure.graph import create_graph_flow
# langgraph_app = create_graph_flow()

def analyze_symptoms(symptoms_text):
    """
    API 키가 없을 때를 대비한 '테스트 모드' 함수입니다.
    실제 LangGraph를 호출하지 않고, 고정된 텍스트 답변을 반환합니다.
    """
    
    # 1. (주석 처리) 실제 LangGraph 호출 부분
    # input_data = {"question": symptoms_text}
    # response_state = langgraph_app.invoke(input_data)
    # final_answer_text = response_state.get("final_answer", "죄송합니다...")
    # return final_answer_text

    # 2. [추가] 가짜 답변 반환 (화면 테스트용)
    dummy_response = f"""
    [테스트 모드 동작 중]
    
    사용자님의 증상: "{symptoms_text}"
    
    현재 OpenAI API 키가 없어서 AI가 실제로 분석할 수는 없지만,
    Django 서버와 프론트엔드 연결은 완벽하게 작동하고 있습니다!
    
    이 메시지가 보인다면:
    1. views.py 연결 성공
    2. services.py 호출 성공
    3. index.html 결과 표시 성공
    
    모든 배관 작업이 완료되었습니다. 
    나중에 API 키만 생기면 주석만 풀어서 바로 연결할 수 있습니다.
    """
    
    return dummy_response.strip()