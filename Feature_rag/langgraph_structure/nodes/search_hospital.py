from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import pool
import re

##############################################
# 주소 문자열을 시도/시군구/도로명/동으로 파싱
###############################################
def parse_region(region: str):
    region_clean = re.sub(r"[\(\),]", " ", region).strip()

    dong = None
    if m := re.search(r"\((.*?)\)", region):
        p = [v.strip() for v in re.split(r"[,、]", m.group(1))]
        dong = next((v for v in p if v.endswith("동")), None)

    pattern = (
        r'(?P<sido>[가-힣]+(?:특별시|광역시|도))?\s*'
        r'(?P<sigungu>[가-힣]+(?:시|군))?\s*'
        r'(?P<gu>[가-힣]+구)?\s*'
        r'(?P<road>[가-힣0-9]+(?:로|길|대로))?'
    )
    parsed = re.match(pattern, region_clean)
    result = parsed.groupdict() if parsed else {}
    result["dong"] = dong
    return result
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
#  중증도별 기준 가중 치 설정 변수 
#######################################
CRITERIA_LIST = [
    "간호인력", "의료인력", "건강보험", "건강보험(환자수)",
    "의료급여", "의료급여(환자수)"
]

WEIGHTS = {
    "HIGH": {"간호인력": 0.30, "의료인력": 0.40, "건강보험": 0.05, "건강보험(환자수)": 0.15, "의료급여": 0.05, "의료급여(환자수)": 0.05},
    "MID":  {"간호인력": 0.35, "의료인력": 0.25, "건강보험": 0.15, "건강보험(환자수)": 0.10, "의료급여": 0.10, "의료급여(환자수)": 0.05},
    "LOW":  {"간호인력": 0.20, "의료인력": 0.10, "건강보험": 0.20, "건강보험(환자수)": 0.20, "의료급여": 0.15, "의료급여(환자수)": 0.15},
}

'''
간호인력 → 간호사 수 / 간호등급 (HIGH일수록 중요)
의료인력 → 의사 수 / 전문의 수 (HIGH일수록 가장 중요)
건강보험 → 건강보험 진료량 (경증일수록 중요)
건강보험(환자수) → 환자 수 기반 지표 (지역 접근성 판단에 가까움)
의료급여 / 의료급여(환자수) → 취약계층 진료량 (경증/중등도에서 의미)

'''

###################################################
# 병원별 최종 점수 계산 함수
########################################################
def calculate_score(grades, severity):
    return sum(
        grade_to_score(g) * WEIGHTS[severity].get(c, 0)
        for c, g in grades.items()
    )

##############################################
# 병원 추천 search node
##############################################
def search_hospital_node(state: GraphState) -> GraphState:
    department, region = state.get("final_department"), state.get("region")
    severity = state.get("severity", "MID")

    parsed = parse_region(region)
    search_keys = [
        parsed.get("road"),
        parsed.get("dong"),
        parsed.get("gu"),
        parsed.get("sigungu"),
    ]

    conn = pool.get_conn()
    hospitals = {}

    try:
        with conn.cursor() as cur:
            base_sql = """
                SELECT 
                    hospital_name, address, medical_specialties,
                    care_grade_basis, care_grade, equip_summary
                FROM hospital_table
                WHERE 1=1
            """
            params = []

            if department:
                base_sql += " AND medical_specialties ILIKE CONCAT('%%', %s, '%%')"
                params.append(department)

            # fallback 검색
            for key in search_keys:
                if not key:
                    continue

                sql = base_sql + " AND address ILIKE CONCAT('%%', %s, '%%');"
                cur.execute(sql, (*params, key))
                rows = cur.fetchall()

                if not rows:
                    continue

                # 병원 데이터 구성
                for name, addr, spec, basis, grade, eq in rows:
                    if name not in hospitals:
                        hospitals[name] = {
                            "hospital_name": name,
                            "address": addr,
                            "medical_specialties": spec,
                            "equip_summary": eq,
                            "care_grade_basis": {c: None for c in CRITERIA_LIST},
                        }
                    hospitals[name]["care_grade_basis"][basis] = grade

                break

    finally:
        pool.put_conn(conn)

    # 후보가 없으면 빈 배열
    if not hospitals:
        return {**state, "hospital_recommend": []}

    # 점수 계산 + 상위 2개만
    ranked = sorted(
        (
            {**info, "score": calculate_score(info["care_grade_basis"], severity)}
            for info in hospitals.values()
        ),
        key=lambda x: x["score"],
        reverse=True
    )

    return {**state, "hospital_recommend": ranked[:2]}

# -----------------------------
# 테스트
# -----------------------------
if __name__ == "__main__":
    result = search_hospital_node({
        "region": "서울시 서초구 헌릉로8길 58",
        "final_department": "외과",
        "severity": "HIGH"
    })
    print(result["hospital_recommend"])
    