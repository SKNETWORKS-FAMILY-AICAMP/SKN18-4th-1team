from langgraph_structure.init_state import GraphState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from langgraph.graph import END
from langgraph_structure.utils import model
import json

# 증상을 의미하는 질문인지, 쓸데없는 질문인지 판별하는 node
def classify_node(state: GraphState) -> GraphState:
    final_answer=""
    chat_prompt = ChatPromptTemplate(
        messages=[
            # system 역할
            SystemMessage(
                content=("""
                    당신은 전문 의학지식을 갖춘 **의료 전문가**입니다.
                    사용자의 질문이 다음 세 가지 중 어디에 속하는지를 구분하세요.
                    
                    1. 이 질문이 무관 질문 (비의료/일반 대화)이면, "service": "irrelevant" 라고 해주세요
                    2️. 사용자가 자신의 증상, 통증, 불편함, 질환 가능성, 의학적 용어 설명에 대해 묘사한 경우 
                        - "service": "symptom" 이고,
                        - 관련된 진료과를 1개 이상 추론하세요. (리스트 형태로)
                    3. 사용자가 입력한 질문이 병원 방문 의도이면, 
                        - "service": "hospital" 이고,
                        - 관련된 진료과를 1개 이상 추론하세요. (리스트 형태로)
                    
                    
                    ### 예시
                    - "두통이 있고 어지러워요" → ["신경과", "이비인후과"]
                    - "명치가 아프고 소화가 안돼요" → ["내과", "소화기내과"]
                    - "허리가 아파요" → ["정형외과", "신경외과"]
                    - "피부에 두드러기가 나요" → ["피부과"]

                    ### 가능한 진료과 목록
                    외과, 예방의학, 정신건강의학과, 신경과/신경외과, 피부과, 안과, 이비인후과, 비뇨의학과, 방사선종양학과, 병리과, 마취통증의학과,
                    기타, 산부인과, 소아청소년과, 응급의학과, 내과
                    
                    ## 출력 형식(JSON)
                    {
                        "service": "irrelevant" or 'symptom' or 'hospital'
                        "department": ["진료과1", "진료과2", ...]  // 관련 없음이면 빈 리스트
                    }
                    """
                )
            ),
            # human 역할
            HumanMessagePromptTemplate.from_template("""
                {question}
            """),
        ]
    )
    llm = model(model_name='gpt-5-nano')
    chain = chat_prompt | llm
    response = chain.invoke({'question': state.get('question')})
    result = json.loads(response.content)
    service = result.get("service", False)
    
    if service == "irrelevant":
        final_answer = "죄송합니다. 조금 더 상세히 설명해주시면 도와드리도록 하겠습니다."    
    return {
        **state,
        "service":service,
        "department": result.get("department"),
        "final_answer": final_answer
    }
    
        
        
def classify_quit(state: GraphState) -> str:
    if state.get("service", "") == "irrelevant":
        return END
    return "search_node"
