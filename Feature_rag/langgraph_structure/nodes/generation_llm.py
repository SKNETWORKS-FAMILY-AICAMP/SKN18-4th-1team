import os, sys # 파일 합칠때는 해당 코드 삭제해도 무방, 경로 잡아주는 코드임
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))) # 파일 합칠때는 해당 코드 삭제해도 무방, 경로 잡아주는 코드임

from langgraph_structure.init_state import GraphState
from langchain_core.prompts import PromptTemplate
from langgraph_structure.utils import model


def _format_hospitals(hospitals: list) -> str:
    if not hospitals:
        return "추천 병원 정보 없음"
    lines = []
    for h in hospitals[:3]:
        name = h.get("hospital_name", "")
        addr = h.get("address", "")
        spec = h.get("medical_specialties", "")
        lines.append(f"- {name} - {addr} ({spec})")
    return "\n".join(lines)


def generation_llm_node(state: GraphState) -> GraphState:
    """이전 노드 결과를 취합하여 최종 답변 생성"""

    question = state.get("question", "")
    department = state.get("final_department") or state.get("department", "")
    disease = state.get("most_likely_disease", "")
    severity = state.get("severity", "")
    relevant_contents = "\n\n".join(state.get("relevant_contents", []))
    hospitals_str = _format_hospitals(state.get("hospitals", []))

    prompt = PromptTemplate.from_template(
        """
        당신은 환자를 돕는 한국어 의료 안내 어시스턴트입니다.
        아래 정보를 바탕으로 친절하고 간결한 최종 답변을 작성하세요.

        [입력]
        - 사용자 질문: {question}
        - 추정 질환: {disease}
        - 중증도: {severity}
        - 권장 진료과: {department}
        - 관련 정보(검색 요약):\n{relevant_contents}
        - 추천 병원:\n{hospitals_str}

        [작성 지침]
        1) 한 문장 요약으로 시작하세요.
        2) 가능한 원인과 주의 증상을 2~3줄로 설명하세요.
        3) 가정 내 관리 팁 또는 병원 방문 기준을 제시하세요.
        4) 권장 진료과와 함께 병원 1~3곳을 불릿으로 제시하세요.
        5) 마지막 줄에 간단한 비의료 조언 면책 문구를 포함하세요.
        """
    )

    llm = model("gpt-5-nano")
    chain = prompt | llm
    resp = chain.invoke({
        "question": question,
        "disease": disease,
        "severity": severity,
        "department": department,
        "relevant_contents": relevant_contents,
        "hospitals_str": hospitals_str,
    })

    return {**state, "final_answer": resp.content}

################################################
# 테스트 코드(아래 코드는 합칠 때 삭제 필요)
################################################
if __name__ == "__main__":
    test_state = GraphState({
        "question": "어제부터 기침이 심하고 가래가 많아요.",
        "most_likely_disease": "감기",
        "severity": "경증",
        "department": "내과",
        "relevant_contents": [
            "감기는 바이러스 감염으로 인해 발생하며 기침, 콧물 등이 나타날 수 있음.",
            "대부분은 휴식과 수분 섭취로 호전됨."
        ],
        "hospitals": [
            {
                "hospital_name": "서울내과의원",
                "address": "서울특별시 강남구 어딘가",
                "medical_specialties": "내과"
            }
        ]
    })

    result = generation_llm_node(test_state)
    print(result["final_answer"])
