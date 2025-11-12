import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import pool


def search_hospital_node(state: GraphState) -> GraphState:
    """사용자 진료과/지역 조건에 맞는 병원 리스트를 DB에서 조회"""
    
    department = state.get("department")
    severity = state.get("severity")       # 예: '경증', '중등도', '중증'
    
    hospitals = []
    conn = pool.getconn()

    '''
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM hospial_table LIMIT 5;") # 
            
    finally:
        pool.putconn(conn)  
    return {
        **state,
        "hospitals":hospitals
    }
    '''
    try:
        with conn.cursor() as cur:
            # 상위 5개 쿼리 선택
            cur.execute("SELECT hospital_name, address, medical_specialties FROM hospital_table LIMIT 5;")
            rows = cur.fetchall()

            for row in rows:
                hospitals.append({
                    "hospital_name": row[0],
                    "address": row[1],
                    "medical_specialties": row[2]
                })

    except Exception as e:
        print(f" DB 조회 오류: {e}")

    finally:
        # 반드시 커넥션 반환해야 커넥션 풀이 고갈되지 않음
        pool.putconn(conn)

    # state 업데이트 후 반환
    return {
        **state,
        "hospitals": hospitals
    }

# 테스트 진행
if __name__ == "__main__":
    from langgraph_structure.init_state import GraphState

    # 테스트용 state 생성
    test_state = GraphState({
        "department": "내과",
        "severity": "중등도"
    })

    print("병원 검색 노드 테스트")

    result_state = search_hospital_node(test_state)

    print("병원 검색 결과:")
    for i, hospital in enumerate(result_state["hospitals"], start=1):
        print(f"{i}. {hospital['hospital_name']} - {hospital['address']} ({hospital['medical_specialties']})")
