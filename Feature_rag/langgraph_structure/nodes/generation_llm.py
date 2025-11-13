from langgraph_structure.init_state import GraphState
from langchain_core.prompts import PromptTemplate
from langgraph_structure.utils import model

def generation_llm_node(state: GraphState) -> GraphState:

    service = state.get("service")
    question = state.get("question")
    llm = model("gpt-5-nano")
    if service == "symptom":
        chain = __symptom_template() | llm
        result = chain.invoke({
        "question": question,
        "relevant_contents": state.get('relevant_contents'),
        })
        
    else:
        chain =__hospital_template() | llm
        result = chain.invoke({
        "question": question,
        "most_likely_disease": state.get("most_likely_disease", ""),
        "severity": state.get("severity", ""),
        "final_department":state.get("final_department", ""),
        "hospital_recommend": state.get("hospital_recommend")

        })


    return {
        **state,
        "final_answer": result.content
    }
    
    
def __symptom_template() :
    template = """
    당신은 전문적인 의료 지식을 바탕으로 사용자에게 안전하고 신뢰할 수 있는 설명을 
    제공하는 **의료 상담 어시스턴트** 입니다.
    --------------------------------------
    [사용자 질문]
    {question}

    [참고 컨텍스트(의학 문서 요약)]
    {relevant_contents}
    --------------------------------------

    ## 답변 생성 규칙 (반드시 준수)

    1. **추측 기반 진단을 금지**  
    - 확정 표현 금지 (“~입니다” X)  
    - 가능성 기반 표현 사용 (“~일 가능성이 있습니다”, “~로 볼 수 있습니다”)

    2. **RAG 기반 근거 반영**  
    - 제공된 컨텍스트가 있다면 그 범위 내에서 설명
    - 컨텍스트 내용이 부족하다면 일반적인 의학적 범위에서만 설명

    3. **증상 분석 구조화**  
    (1) 증상 요약  
    (2) 가능한 원인 또는 관련 질환 후보 (우선순위 높은 순)  
    (3) 위험 신호 여부  
    (4) 관리 방법  
    (5) 필요 시 적절한 진료과  

    4. **위험 신호 규칙**
        - 호흡곤란, 경련, 갑작스런 의식 변화 등 응급 수준만 주의 표시

    5. **사용자 친화적 표현**
        - 전문 용어는 간단한 부연 설명 포함
        - 불필요하게 긴 설명 금지

    ## 출력 형식
    - 증상 요약  
    - 가능한 원인/질환 후보  
    - 위험 신호 여부  
    - 도움이 되는 관리 방법  
    - 필요 시 진료과 안내  
    """
    return PromptTemplate.from_template(template)

def __hospital_template():
    template ="""
            당신은 '증상 기반 병원 추천 전문 어시스턴트'입니다.
            아래 정보는 이미 전문 알고리즘을 통해 판단된 사용자 상태이며,
            당신은 이 정보를 기반으로 추천된 병원을 사용자에게 이해하기 쉽게 설명해야 합니다.

            --------------------------------------
            [사용자 질문]
            {question}

            [사용자 증상 분석 결과]
            - 의심 질환: {most_likely_disease}
            - 중증도: {severity}
            - 관련 진료과: {final_department}

            [추천된 병원 리스트 (점수 높은 순)]
            {hospital_recommend}
            --------------------------------------

            ## 작성 규칙
            1. ** 병원 설명 **
                - 왜 적합한지
                - 진료과와의 연결성
                - 실제 데이터에 존재하는 근거만 사용 (간호등급, 장비, 의료진 등)

            2. 간호등급은 의미 기반으로 변환하여 설명:
                예: "간호 인력이 충분하여 환자 케어가 빠릅니다."

            3. 새로운 의학적 판단을 하지 말 것
            - 이미 나온 {most_likely_disease}, {severity}, {final_department}만 사용

            4. 마지막에 친절한 의료 안내 문구 포함
            예: "정확한 진단은 의료진의 진료를 통해 확인할 수 있습니다."

            ## 출력 형식

            - 추천 병원 1~2개 + 추천 이유
            - 진료과 적합성 설명
            - 마무리 안내 문구
    """
    return PromptTemplate.from_template(template)
