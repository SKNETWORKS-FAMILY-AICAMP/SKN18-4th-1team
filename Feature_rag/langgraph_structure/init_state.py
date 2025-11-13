from typing import Any, Dict, List, TypedDict


class GraphState(TypedDict):
    # 사용자 input 
    question: str
    service: str
    region: str # 지역
    
    # 검색 관련
    search_chunks:List
    mean_similarity_score: float
    
    # 검색 평가 관련
    relevant_source:List[str]
    relevant_category: List[str]
    relevant_contents: List[str]
    retrieval_question: bool        
    avg_relevance: float
    feedback_messages: str
    max_token:str
    
    # 증상 판단
    most_likely_disease:str
    severity:str
    final_department:str
    
    # 병원 찾기
    hospital_recommend:List[Dict]
    #최종 답볍
    final_answer:str
