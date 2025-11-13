import os
from dotenv import load_dotenv

# .env 파일을 먼저 로드해야 utils.py의 connection pool이 올바른 CONNECTION_STRING을 사용할 수 있습니다
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=env_path, encoding='utf-8')
from typing import Any, Dict, List, Optional
from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import pool

import traceback

def _parse_address(address: str) -> Dict[str, Optional[str]]:
    """주소 문자열을 파싱하여 시/도, 시/군/구, 동/읍/면을 추출합니다.
    
    한국 주소 형식: "서울특별시 강남구 역삼동" 또는 "경기도 성남시 분당구 정자동"
    """
    if not address:
        return {"province": None, "city": None, "dong": None}
    
    # 주소를 공백으로 분리
    parts = [p.strip() for p in address.split() if p.strip()]
    
    province = None
    city = None
    dong = None
    
    if len(parts) >= 1:
        province = parts[0]
    if len(parts) >= 2:
        city = parts[1]
    if len(parts) >= 3:
        dong = parts[2]
    
    return {"province": province, "city": city, "dong": dong}


def _fetch_hospitals_from_db(
    address_token: Optional[str] = None, 
    department_token: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """사용자 위치에따른 DB 조회 헬퍼 (성능 최적화 버전).

    파라미터:
    - address_token: 사용자가 입력한 현재 위치(예: 동/읍/면 또는 시/구) 문자열.
        prefix 검색을 사용하여 인덱스 활용도를 높입니다.
    - department_token: 진료과 필터링용 토큰 (medical_specialties 컬럼에서 검색)
    - limit: 반환할 최대 결과 수 (기본값: 20)

    성능 최적화:
    - ILIKE '%token%' 대신 prefix 검색 사용 (인덱스 활용 가능)
    - LIMIT 절 추가로 불필요한 데이터 스캔 방지
    - 작은 범주부터 검색하여 조기 종료
    """
    
    query_template = """
        SELECT 
            hospital_name, 
            address, 
            medical_specialties, 
            care_grade, 
            care_grade_basis, 
            equip_summary
        FROM hospital_table 
        WHERE {where} 
        ORDER BY hospital_name
        LIMIT %s;
    """

    where_clauses: List[str] = []
    params: List[Any] = []
    
    # 주소 검색: prefix 검색 사용 (인덱스 활용 가능)
    # "서울특별시"로 시작하는 주소 검색 -> 인덱스 활용
    # ILIKE '%서울%' 대신 address LIKE '서울%' 사용
    if address_token:
        # prefix 검색으로 변경 (인덱스 활용 가능)
        where_clauses.append("address ILIKE %s")
        params.append(f"{address_token}%")
    
    # 진료과 검색: 부분 매칭 (데이터가 적으므로 ILIKE 사용)
    if department_token:
        where_clauses.append("medical_specialties ILIKE %s")
        params.append(f"%{department_token}%")

    where = " AND ".join(where_clauses) if where_clauses else "TRUE"
    params.append(limit)  # LIMIT 파라미터 추가

    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            q = query_template.format(where=where)
            cur.execute(q, params)
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]
            results = [dict(zip(cols, r)) for r in rows]
            return results
    except Exception as e:
        traceback.print_exc()
        return []
    finally:
        try:
            pool.putconn(conn)
        except Exception:
            pass

def _fetch_departments_from_db(
    keyword: Optional[str] = None,
    limit: int = 30
) -> List[str]:
    """
    hospital_table에서 진료과 목록을 중복 없이 조회합니다.

    파라미터:
    - keyword: 부분 검색용 문자열 (예: "내과", "정신")
    - limit: 반환할 최대 개수 (기본값: 30)

    반환값:
    - 진료과 문자열 리스트
    """
    query = """
        SELECT DISTINCT medical_specialties
        FROM hospital_table
        WHERE medical_specialties IS NOT NULL
          AND medical_specialties <> ''
          AND medical_specialties ILIKE %s
        ORDER BY medical_specialties
        LIMIT 20
    """

    params: List[Any] = []
    where_clause = ""

    if keyword:
        where_clause = "AND medical_specialties ILIKE %s"
        params.append(f"%{keyword}%")

    q = query.format(where=where_clause)
    params.append(limit)

    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(q, (f"%{keyword}%",))
            rows = cur.fetchall()
        return [r[0] for r in rows]
    except Exception as e:
        traceback.print_exc()
        return []
    finally:
        try:
            pool.putconn(conn)
        except Exception:
            pass


def search_department_node(state: GraphState) -> GraphState:
    """
    사용자가 입력한 키워드 또는 질문에서 진료과를 검색합니다.

    기대 사항:
    - state["query"] 또는 state["user_input"]에 사용자의 문장이 포함되어야 함.
      예: "정신과 가고 싶어요", "이비인후과 잘하는 병원 알려줘"
    - LLM 기반 분류를 하지 않고, DB에 있는 진료과명을 키워드로 단순 검색합니다.

    반환:
    - state["departments"]: DB에 존재하는 진료과 목록 (문자열 리스트)
    """
    user_text = state.get("query") or state.get("user_input")
    if not user_text:
        return {**state, "departments": []}

    # 사용자 입력에서 한글 단어만 추출
    import re
    tokens = re.findall(r"[가-힣]+", user_text)
    departments_found: List[str] = []

    # DB에서 모든 진료과 가져오기 (성능 고려하여 300개 제한)
    all_departments = _fetch_departments_from_db(limit=300)

    # 입력된 단어 중 진료과명과 일치하거나 포함된 항목 찾기
    for token in tokens:
        for dept in all_departments:
            if token in dept:
                departments_found.append(dept)

    # 중복 제거
    departments_found = list(dict.fromkeys(departments_found))

    # 결과가 없을 경우: 전체 진료과 중 일부 추천
    if not departments_found:
        departments_found = _fetch_departments_from_db(limit=10)

    return {**state, "departments": departments_found}



def search_hospital_node(state: GraphState) -> GraphState:
    """예측된 진료과(department)와 행정구역에 맞는 병원을 반환합니다.

    기대 사항:
    - `state`에는 이전 노드에서 예측된 `department`가 포함되어 있어야 합니다.
    - 행정 구역 키를 우선 사용: `dong`, `city`, `province`.
    만약 존재하지 않으면, `address`를 제공할 수 있으며,
    단순히 "province city dong ..." 형식으로 파싱합니다.

    동작 방식:
    - DB에서 병원 데이터를 주소와 진료과(medical_specialties)로 필터링합니다.
    - 병원 주소와 행정 구역을 비교하며 순서대로 dong → city → province 매칭을 시도합니다.
    - 매칭되는 병원들을 반환합니다. (좌표나 거리 비교는 수행하지 않습니다)
    - 반환되는 병원 정보에는 name, address, department(medical_specialties), care_grade, care_grade_basis, equip_summary가 포함됩니다.
    """
    department = state.get("department")
    address_text = state.get("address") or state.get("user_address")

    # NOTE: For this flow we prefer administrative-region matching rather than
    # geographic coordinate distance. The expected matching order is:
    #   1) dong (동/읍/면) level
    #   2) city (시/군/구) level
    #   3) province (도/광역시) level
    # If state provides explicit keys `province`, `city`, `dong` we use them.
    # Otherwise we attempt a naive parse of `address_text` (split by whitespace)
    # assuming the order "province city dong ...".

    province = state.get("province")
    city = state.get("city")
    dong = state.get("dong")

    # 주소 파싱: state에 명시적으로 없으면 address_text에서 파싱
    if not any((province, city, dong)) and address_text:
        parsed = _parse_address(address_text)
        province = province or parsed.get("province")
        city = city or parsed.get("city")
        dong = dong or parsed.get("dong")

    # Query DB directly using WHERE clause priority to avoid loading entire table.
    matched: List[Dict[str, Any]] = []
    match_level = "any"

    # 검색 순서: dong -> city -> province (작은 범주에서 큰 범주로)
    # 작은 범주부터 검색하여 조기 종료로 성능 향상
    # 주소를 조합하여 prefix 검색으로 인덱스 활용도 향상
    
    # 동 단위 검색: 주소를 조합하여 "서울특별시 강남구 역삼동" 형식으로 prefix 검색
    if dong:
        # 주소 조합: province + city + dong
        if province and city:
            combined_address = f"{province} {city} {dong}"
        elif city:
            combined_address = f"{city} {dong}"
        else:
            combined_address = dong
        
        rows = _fetch_hospitals_from_db(address_token=combined_address, department_token=department, limit=20)
        if rows:
            matched = rows
            match_level = "dong"

    # 시/군/구 단위 검색: "서울특별시 강남구" 형식으로 prefix 검색
    if not matched and city:
        if province:
            combined_address = f"{province} {city}"
        else:
            combined_address = city
        
        rows = _fetch_hospitals_from_db(address_token=combined_address, department_token=department, limit=20)
        if rows:
            matched = rows
            match_level = "city"

    # 시/도 단위 검색: "서울특별시" prefix 검색
    if not matched and province:
        rows = _fetch_hospitals_from_db(address_token=province, department_token=department, limit=20)
        if rows:
            matched = rows
            match_level = "province"

    # If still nothing, return empty list (avoid returning whole table)
    if not matched:
        return {**state, "hospitals": []}

    # Build output entries (no coordinate-based distance)
    out: List[Dict[str, Any]] = []
    for h in matched:
        out.append({
            "name": h.get("hospital_name"),
            "address": h.get("address"),
            "department": h.get("medical_specialties"),
            "care_grade": h.get("care_grade"),
            "care_grade_basis": h.get("care_grade_basis"),
            "equip_summary": h.get("equip_summary"),
            #"matched_level": match_level,
        })

    # Limit results to top 10 by default (caller can slice)
    out = out[:10]

    return {**state, "hospitals": out}


# 간단한 한글 프롬프트 템플릿 (SQL에 저장된 병원 데이터는 벡터화하지 않음)
# 이 노드는 RDB에서 직접 WHERE로 조회하여 병원을 찾습니다.
# 예시 프롬프트/설명:
# "사용자 주소와 예측된 진료과에 따라 가까운 병원을 추천합니다. 먼저 동(읍/면)이 있으면 그 수준에서, 없으면 시/군/구, 없으면 도(광역시) 수준에서 주소 포함 여부로 필터합니다. 좌표 기반 거리는 사용하지 않습니다."


if __name__ == "__main__":
    import json

    address_token = "서울특별시 강서구 등촌로"
    department_keyword = "안과"  # 🔹 여기서 원하는 진료과 키워드
    print("="*60)
    print("🔍 병원 / 진료과 검색 테스트")
    print("="*60)

    print(f"\n📍 검색 주소: {address_token}")
    print(f"🩺 진료과 키워드: {department_keyword}\n")

    # DB 연결
    conn = pool.getconn()
    try:
        # 1️⃣ 병원 검색
        hospitals = _fetch_hospitals_from_db(address_token=address_token)
        print(f"✅ 검색된 병원: {len(hospitals)}개\n")
        
        # 2️⃣ 진료과 검색
        departments = _fetch_departments_from_db(keyword=department_keyword)
        print(f"✅ 검색된 진료과: {departments}\n")

        # 3️⃣ 최종 결과: 병원 정보 + 관련 진료과 표시
        final_result = []
        for h in hospitals:
            final_result.append({
                "hospital_name": h.get("hospital_name"),
                "address": h.get("address"),
                "department": h.get("medical_specialties"),  # DB에 저장된 진료과
                "matched_department": department_keyword,    # 사용자가 검색한 키워드
                "care_grade": h.get("care_grade"),
                "care_grade_basis": h.get("care_grade_basis"),
                "equip_summary": h.get("equip_summary")
            })

        print("🔹 최종 결과 (병원 + 검색 진료과 포함):")
        print(json.dumps(final_result[:10], ensure_ascii=False, indent=2))  # 상위 10개만
    finally:
        pool.putconn(conn)

