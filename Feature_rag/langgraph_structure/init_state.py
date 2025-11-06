from typing import Any, Dict, List, TypedDict


class GraphState(TypedDict):
    # 사용자 input 
    question: str
    need_quit: bool
    
    # 검색 관련
    
    # 검색 평가 관련
    relevant_category: List[str]
    relevant_contents: List[str]
    retrieval_question: bool
    avg_relevance: float
    feedback_messages: str
    max_token:str
