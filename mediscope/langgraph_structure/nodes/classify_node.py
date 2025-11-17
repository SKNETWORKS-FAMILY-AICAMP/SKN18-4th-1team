from langgraph_structure.init_state import GraphState
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langgraph.graph import END
from langgraph_structure.utils import model
import json

# 증상을 의미하는 질문인지, 쓸데없는 질문인지 판별하는 node
def classify_node(state: GraphState) -> GraphState:

    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            """
            당신은 전문 의학지식을 갖춘 **의료 전문가**입니다.

            아래는 사용자의 기본 정보입니다:
            {survey_result}

            이 정보를 참고하여 사용자 질문이 다음 세 가지 중 어디에 속하는지 판단하세요.

            1. 이 질문이 무관 질문(비의료/일반 대화)이면  
            - "service": "irrelevant"  
            - "department": [] 로 표시하세요.

            2. 사용자가 증상·통증·불편함·질환 가능성을 묘사한 경우  
            - "service": "symptom"
            - 가능한 진료과 목록에서 관련된 진료과를 1개 이상 선택하세요. 

            3. 사용자가 병원 방문 의도를 드러낸 경우  
            - "service": "hospital"
            - 가능한 진료과 목록에서 1개 이상 선택하세요.

            ---

            ### 가능한 진료과 목록
            외과, 예방의학, 정신건강의학과, 신경과/신경외과, 피부과, 안과,
            이비인후과, 비뇨의학과, 방사선종양학과, 병리과, 마취통증의학과, 기타,
            산부인과, 소아청소년과, 응급의학과, 내과

            반드시 위 목록 안에서만 선택하세요.

            ---

            ## 출력 형식(JSON)
            {{
                "service": "irrelevant" or "symptom" or "hospital",
                "department": ["진료과1", "진료과2"]
            }}
            """
        ),

        HumanMessagePromptTemplate.from_template("{question}")
    ])
    
    # LLM
    llm = model(model_name='gpt-5-nano', reasoning_effort="low")
    chain = chat_prompt | llm

    # 동적 값 (state에서 가져오기)
    response = chain.invoke({
        'question': state.get('question'),
        'survey_result': state.get('survey_result'),
    })

    result = json.loads(response.content)
    service = result.get("service", False)
    
    if service == "irrelevant":
        final_answer = "죄송합니다. 조금 더 상세히 설명해주시면 도와드리도록 하겠습니다."
    else:
        final_answer = ""  

    return {
        **state,
        "service": service,
        "department": result.get("department"),
        "final_answer": final_answer
    }
        
        
def classify_quit(state: GraphState) -> str:
    if state.get("service", "") == "irrelevant":
        return END
    return "rewrite_question_node"
