from langchain_core.prompts import PromptTemplate
from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import model
import json

def judgment_symtom_node(state:GraphState)-> GraphState:
    
    template =  PromptTemplate.from_template('''
        당신은 환자의 상태를 종합적으로 판단하는 **의료 전문가**입니다.  
        아래에 주어진 ‘사용자 증상’과 ‘관련 질환 후보 정보’를 근거로,  
        가장 가능성이 높은 질환을 선택하고, 중증도 및 진료과를 최종 확정하세요.
        ---
        ## 입력 정보
        ### 사용자 증상:
        {question}

        ### 질환 후보 목록 (RAG 검색 결과)
        {relevant_contents}
        ---
        ## 판단 기준
        1 **질환 선정**
            - 증상 표현, 연관 부위, 발병 원인, 동반 증상 등을 종합적으로 고려하세요.
            - 한 가지 질환만 선택합니다.

        2. **중증도 판단**
            - 경증: 가벼운 증상, 일상생활 가능, 자연 호전 가능
            - 중등도: 지속적이거나 불편을 유발, 치료 필요
            - 중증: 생명 위협 또는 응급 치료 필요

        3️. **진료과 확정**
            - 선택된 질환의 대표 진료과를 지정하세요.
        ---
        ## 출력 형식 (JSON)
        {{
            "most_likely_disease": "질환명",
            "severity": "경증 / 중등도 / 중증 중 하나",
            "final_department": "진료과명"
        }}
    ''')
    
    llm = model(model_name='gpt-5-mini')
    chain = template | llm
    response = chain.invoke(
        {'question': state.get('question'), 'relevant_contents': state.get('relevant_contents')})
    result = json.loads(response.content)
    return {
        **state,
        "most_likely_disease": result.get("most_likely_disease",""),
        "severity":result.get("severity",""),
        "final_department":result.get("final_department","")
    }
