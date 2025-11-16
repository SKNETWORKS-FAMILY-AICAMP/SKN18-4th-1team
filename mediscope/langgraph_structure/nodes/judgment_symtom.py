from langchain_core.prompts import PromptTemplate
from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import model
import json

def judgment_symtom_node(state:GraphState)-> GraphState:
    
    template =  PromptTemplate.from_template('''
        당신은 전문 의료 전문가입니다.  
        주어진 정보를 바탕으로 가장 가능성이 높은 질환 1개, 중증도, 최종 진료과를 판단하세요.

        ## 입력
        - 증상: {question}
        - 사용자 정보: {survey_result}
        - 질환 후보: {relevant_contents}
        - 진료과 후보: {relevant_category}

        ## 규칙
        1) **질환 선정**  
        - 증상과 사용자 정보를 가장 잘 설명하는 질환 1개 선택.

        2) **중증도 판단**  
        - LOW / MID / HIGH 중 하나 선택.

        3) **진료과 확정(리스트 형태)**
        - 반드시 진료과 후보 목록 안에서만 선택해야 합니다.
        - 후보 목록의 진료과가 특정 세부 진료과에서 주로 치료되는 것이 명확하면  
        세부 진료과로 확장하여 선택할 수 있습니다.
        - 확장하는 경우에는 반드시 원래 1차 진료과도 함께 포함하여  
        ["1차 진료과", "세부 진료과"] 형태의 리스트로 반환하세요.
        - 세부 진료과를 특정하기 어려운 경우, 후보 목록의 1차 진료과만 단독으로 반환하세요.
        ---

        ## 출력 형식(JSON)
        {{
            "most_likely_disease": [],
            "severity": "",
            "final_department": ""
        }}
    ''')
    llm = model(model_name='gpt-5-nano', reasoning_effort="medium")
    chain = template | llm
    response = chain.invoke(
        {'question': state.get('question'), 
        'survey_result':state.get("survey_result"),
        'relevant_category': state.get("relevant_category")or state.get("department"),
        'relevant_contents': state.get("relevant_contents") 
        })
    result = json.loads(response.content)
    return {
        **state,
        "most_likely_disease": result.get("most_likely_disease",[]),
        "severity":result.get("severity",""),
        "final_department":result.get("final_department","")
    }
