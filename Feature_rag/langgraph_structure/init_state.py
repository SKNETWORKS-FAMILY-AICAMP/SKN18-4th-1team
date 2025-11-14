from typing import Any, Dict, List, TypedDict


class GraphState(TypedDict):
    # 사용자 input 
    question: str
    health_profile: dict
    survey_result: dict
    region : str
    
    # memory 관련
    summary: str
    
    # classification 관련
    service: str # 증상분류, 병원찾기
    department: List[str]
    
    # 검색 관련
    search_chunks: List[Dict[str, Any]]
    mean_similarity_score: float # 평균 유사도 점수
    
    # 검색 평가 관련
    relevant_source:List[Dict] # 평가된 출처
    relevant_category: List[str] # 평가된 카테고리
    relevant_contents: List[str] # 평가된 내용
    retrieval_question: bool   #     
    avg_relevance: float # 평균 관련성 점수
    feedback_messages: str # 피드백 메시지
    max_token:str # 최대 토큰 수(질문 재작성 1번 실행)
    
    # 증상 판단
    most_likely_disease:str
    severity:str
    final_department:str
    
    # 병원 찾기
    hospital_recommend:List[Dict]
    
    #최종 답볍
    final_answer:str
