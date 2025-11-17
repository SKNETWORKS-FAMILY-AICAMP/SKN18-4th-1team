from typing import Any, Dict, List, TypedDict


class GraphState(TypedDict):
    # 사용자 input 
    question: str
    survey_result: str
    region : str
    
    # 질문 재장성
    rewrite_question:str
    
    # memory 관련
    summary: str
    
    # classification 관련
    service: str # 증상분류, 병원찾기
    department: List[str]
    
    # 검색 관련
    search_chunks: List[Dict[str, Any]]
    mean_similarity_score: float # 평균 유사도 점수
    
    # 검색 평가 관련
    relevant_source:List[str] # 평가된 출처
    relevant_category: List[str] # 평가된 카테고리
    relevant_contents: List[str] # 평가된 내용
    check_web: bool   #     
    avg_relevance: float # 평균 관련성 점수
    
    # web_search
    web_mean_score: float
    check_quit: bool
    # 증상 판단
    most_likely_disease:str
    severity:str
    final_department:List[str]
    
    # 병원 찾기
    hospital_recommend:List[Dict]
    
    #최종 답볍
    final_answer:str


# 프롬프트 바꾸기
# survey_response -> 사용자 입력 가져오기 
