from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import pool
import re

##############################################
# 주소 문자열을 시도/시군구/도로명/동으로 파싱
###############################################
def parse_region(region: str):
    region_clean = re.sub(r"[\(\),]", " ", region).strip()

    emd_paren = None
    if m := re.search(r"\((.*?)\)", region):
        p = [v.strip() for v in re.split(r"[,、]", m.group(1))]
        emd_paren = next((v for v in p if v.endswith(("동", "읍", "면", "리"))), None)

    pattern = (
        r'(?P<sido>[가-힣]+(?:특별시|광역시|도))?\s*'
        r'(?P<sigungu>[가-힣]+(?:시|군))?\s*'
        r'(?P<gu>[가-힣]+구)?\s*'
        r'(?P<emd>[가-힣]+(?:읍|면|동))?\s*'
        r'(?P<road>[가-힣0-9]+(?:로|길|대로))?'
    )
    parsed = re.match(pattern, region_clean)
    result = parsed.groupdict() if parsed else {}
    if emd_paren and not result.get("emd"):
        result["emd"] = emd_paren
    return result

##############################################
# 주소: 좁은 범위 → 넓은 범위로 fallback 검색 조건
###############################################
def build_search_conditions(parsed):

    order = ["road", "emd", "gu", "sigungu", "sido"]
    # 실제 값이 있는 항목만 추출
    parts = [parsed[o] for o in order if parsed.get(o)]
    return [parts[i:] for i in range(len(parts))]


#############################################
# 진료과 문자열 정규화
############################################
def normalize_dept(raw):
    """
    raw: 병원 department 문자열 OR 리스트 모두 지원
    예: "내과/소화기내과"
        ["내과", "소화기내과"]
    """
    if not raw:
        return []

    # 1) 리스트면: 각 요소를 문자열로 변환 후 공백 제거 후 평탄화
    if isinstance(raw, list):
        parts = []
        for item in raw:
            if not item:
                continue
            parts.extend(re.split(r"[ ,/·\|\n\t]+", str(item)))
    else:
        # 2) 문자열로 들어오면 그대로 split
        parts = re.split(r"[ ,/·\|\n\t]+", str(raw))

    # 정제
    return [p.strip() for p in parts if p.strip()]

######################################################
# care_grade 점수 변환 점수
# --> 1~7은 등급 점수, A/S는 중간값(50) 처리
#########################################################
def grade_to_score(v):
    if not v:
        return 50
    v = str(v).upper()
    if v.isdigit() and 1 <= int(v) <= 7:
        return (8 - int(v)) * 15
    return 50

########################################
#  가중 치 설정 변수 
#######################################
CRITERIA_LIST = [
    "간호인력", "의료인력", "건강보험", "건강보험(환자수)",
    "의료급여", "의료급여(환자수)"
]

SEVERITY_WEIGHTS = {
    "HIGH": {"간호인력": 0.30, "의료인력": 0.40, "건강보험": 0.05, "건강보험(환자수)": 0.15, "의료급여": 0.05, "의료급여(환자수)": 0.05},
    "MID":  {"간호인력": 0.35, "의료인력": 0.25, "건강보험": 0.15, "건강보험(환자수)": 0.10, "의료급여": 0.10, "의료급여(환자수)": 0.05},
    "LOW":  {"간호인력": 0.20, "의료인력": 0.10, "건강보험": 0.20, "건강보험(환자수)": 0.20, "의료급여": 0.15, "의료급여(환자수)": 0.15},
}

# 거리 기반 점수 (레벨 ↘ = 가까움)
DIST_LEVEL_SCORE = {
        0: 100,
        1: 80,
        2: 60,
        3: 40,
        4: 20
    }

SEVERITY_RATIO = {
    "HIGH": (0.8, 0.2),   # HIGH → 의료역량 80%, 거리 20%
    "MID":  (0.5, 0.5),
    "LOW":  (0.2, 0.8)    # LOW → 거리 60%, 의료역량 40%
}

###################################################
# 병원별 최종 점수 계산 함수
########################################################
def calculate_score(grades, severity):
    return sum(
        grade_to_score(g) * SEVERITY_WEIGHTS[severity].get(c, 0)
        for c, g in grades.items()
    )

##############################################
# 병원 추천 search node
##############################################
def search_hospital_node(state: GraphState) -> GraphState:
    dept_list = state.get("final_department", [])
    region = state.get("region")
    severity = state.get("severity")

    parsed = parse_region(region)
    search_conditions = build_search_conditions(parsed)

    conn = pool.getconn()
    hospitals = {}

    try:
        with conn.cursor() as cur:
            base_sql = """
                SELECT 
                    hospital_name, address, department,
                    care_grade_basis, care_grade, equip_summary
                FROM hospital_table
                WHERE {where}
            """

            for level, cond in enumerate(search_conditions):
                conds = " AND ".join("address ILIKE %s" for _ in cond)
                params = [f"%{c}%" for c in cond]
                sql = base_sql.format(where=conds)

                cur.execute(sql, params)
                rows = cur.fetchall()

                for name, addr, spec, basis, grade, eq in rows:
                    hosp_depts = normalize_dept(spec)

                    if not any(d in hosp_depts for d in dept_list):
                        continue

                    if name not in hospitals:
                        hospitals[name] = {
                            "hospital_name": name,
                            "address": addr,
                            "hospital_depts_raw": spec,
                            "equip_summary": eq,
                            "level": level, 
                            "care_grade_basis": {c: None for c in CRITERIA_LIST}
                        }

                    hospitals[name]["care_grade_basis"][basis] = grade

    finally:
        pool.putconn(conn)

    if not hospitals:
        return {**state, "hospital_recommend": []}

    # 최종 점수 계산
    ranked = []
    for info in hospitals.values():
        care_score = calculate_score(info["care_grade_basis"], severity)
        dist_score = DIST_LEVEL_SCORE.get(info["level"], 20)

        care_w, dist_w = SEVERITY_RATIO[severity]
        final_score = care_score * care_w + dist_score * dist_w


        ranked.append({**info, "score": final_score})

    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)

    return {**state, "hospital_recommend": ranked[:3]}

'''
if __name__ == "__main__":
    test_state = {
        "final_department": ["내과"],
        "region": "서울특별시 강남구 청담동",
        "severity": "HIGH"
    }

    result = search_hospital_node(test_state)
    print(result["hospital_recommend"])
'''
