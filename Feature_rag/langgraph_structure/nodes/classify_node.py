from langgraph_structure.init_state import GraphState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from langgraph.graph import END
from langgraph_structure.utils import model
import json

# 증상을 의미하는 질문인지, 쓸데없는 질문인지 판별하는 node
def classify_node(state: GraphState) -> GraphState:
    chat_prompt = ChatPromptTemplate(
        messages=[
            # system 역할
            SystemMessage(
                content=("""
                    당신은 전문 의학지식을 갖춘 **의료 전문가**입니다.
                    사용자의 질문이 다음 세 가지 중 어디에 속하는지를 구분하세요.

                    1. 이 질문이 무관 질문(비의료/일반 대화)이면  
                    - "service": "irrelevant"  
                    - "department": [] 로 표시하세요.

                    2. 사용자가 자신의 증상, 통증, 불편함, 질환 가능성, 의학적 용어 설명을 묘사한 경우  
                    - "service": "symptom"  
                    - “가능한 진료과 목록” 중에서만 관련 있는 진료과를 하나 이상 선택하세요.  
                    - 목록에 없는 진료과는 절대 출력하면 안 됩니다.

                    3. 사용자가 병원 방문 의도를 드러낸 경우  
                    - "service": "hospital"  
                    - “가능한 진료과 목록” 중에서만 관련 있는 진료과를 하나 이상 선택하세요.

                    ---

                    ### 예시
                    - "두통이 있고 어지러워요" → ["신경과/신경외과", "이비인후과"]
                    - "명치가 아프고 소화가 안돼요" → ["내과"]
                    - "허리가 아파요" → ["외과", "신경과/신경외과"]
                    - "피부에 두드러기가 나요" → ["피부과"]

                    ---

                    ### 가능한 진료과 목록 (이 목록에서만 선택)
                    외과, 예방의학, 정신건강의학과, 신경과/신경외과, 피부과, 안과, 이비인후과, 비뇨의학과, 
                    방사선종양학과, 병리과, 마취통증의학과, 기타, 산부인과, 소아청소년과, 응급의학과, 내과

                    ※ 반드시 위 목록에 포함되지 않은 진료과는 절대 출력하지 마세요.
                    * 해당하는 진료과가 없다면 빈 리스트로 출력해주세요.

                    ---

                    ## 출력 형식(JSON)
                    {
                        "service": "irrelevant" or "symptom" or "hospital",
                        "department": ["진료과1", "진료과2", ...]
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
    llm = model(model_name='gpt-5-nano', reasoning_effort="low")
    chain = chat_prompt | llm
    response = chain.invoke({'question': state.get('question')})
    result = json.loads(response.content)
    service = result.get("service", False)
    
    if service == "irrelevant":
        final_answer = "죄송합니다. 조금 더 상세히 설명해주시면 도와드리도록 하겠습니다."
    else:
        final_answer = ""  
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
