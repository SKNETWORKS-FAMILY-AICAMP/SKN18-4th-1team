import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import pool


def _addr_prefix(addr: str) -> tuple[str, str, str]:
    """주소의 앞 1~3개 행정구역 토큰을 단순 분리"""
    if not addr:
        return "", "", ""
    parts = addr.strip().split()
    a = parts[0] if len(parts) > 0 else ""
    b = parts[1] if len(parts) > 1 else ""
    c = parts[2] if len(parts) > 2 else ""
    return a, b, c


def search_hospital_node(state: GraphState) -> GraphState:
    """사용자 진료과/지역 조건에 맞는 병원 리스트를 DB에서 조회"""

    # 입력: 진료과(우선은 최종 확정 진료과), 사용자 주소(옵션)
    department = state.get("final_department") or state.get("department", "")
    user_addr = state.get("user_address") or state.get("address") or ""

    hospitals: list[dict] = []
    conn = pool.getconn()

    # 주소 단순 전처리 → LIKE 패턴용 프리픽스 생성
    a, b, c = _addr_prefix(user_addr)
    like3 = f"{a} {b} {c}%" if a and b and c else None
    like2 = f"{a} {b}%" if a and b else None
    like1 = f"{a}%" if a else None

    # 진료과 필터 (없으면 전체)
    dept_pattern = f"%{department}%" if department else None

    try:
        with conn.cursor() as cur:
            # 간단 근접도 점수(주소 접두 일치 개수)를 이용해 정렬
            sql = (
                """
                SELECT hospital_name, address, medical_specialties,
                       CASE
                         WHEN %s IS NOT NULL AND address LIKE %s THEN 3
                         WHEN %s IS NOT NULL AND address LIKE %s THEN 2
                         WHEN %s IS NOT NULL AND address LIKE %s THEN 1
                         ELSE 0
                       END AS score
                FROM hospital_table
                WHERE (%s IS NULL OR medical_specialties ILIKE %s OR medical_specialties = '-')
                ORDER BY score DESC, hospital_name
                LIMIT 5;
                """
            )

            params = [
                like3, like3 or "",  # for CASE 3
                like2, like2 or "",  # for CASE 2
                like1, like1 or "",  # for CASE 1
                dept_pattern, dept_pattern or "",
            ]

            cur.execute(sql, params)
            rows = cur.fetchall()

            for name, addr, spec, _score in rows:
                hospitals.append({
                    "hospital_name": name,
                    "address": addr,
                    "medical_specialties": spec,
                })

    except Exception as e:
        print(f" DB 조회 오류: {e}")
    finally:
        pool.putconn(conn)

    return {**state, "hospitals": hospitals}

# 테스트 진행
if __name__ == "__main__":
    from langgraph_structure.init_state import GraphState

    # 테스트용 state 생성
    test_state = GraphState({
        "department": "외과",
        "severity": "중등도",
        "user_address": "서울특별시 서초구"
    })

    print("병원 검색 노드 테스트")

    result_state = search_hospital_node(test_state)

    print("병원 검색 결과:")
    for i, hospital in enumerate(result_state["hospitals"], start=1):
        print(f"{i}. {hospital['hospital_name']} - {hospital['address']} ({hospital['medical_specialties']})")
