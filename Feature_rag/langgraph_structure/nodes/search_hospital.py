from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import pool


def search_hospital_node(state: GraphState) -> GraphState:
    """사용자 진료과/지역 조건에 맞는 병원 리스트를 DB에서 조회"""
    
    department = state.get("department")
    severity = state.get("severity")       # 예: '경증', '중등도', '중증'
    
    hospitals = []
    conn = pool.getconn() 
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM hospial_table LIMIT 5;") # 
            
    finally:
        pool.putconn(conn)  
    return {
        **state,
        "hospitals":hospitals
    }