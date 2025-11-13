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
                    사용자가 입력한 질문이 '병원 증상'과 관련된 내용인지 먼저 판단하고,  
                    관련 있다면 해당 증상과 가장 밀접한 진료과를 판단하세요.
                    
                    ### 가능한 진료과 예시
                    내과, 소화기내과, 호흡기내과, 심장내과, 외과, 정형외과, 신경외과, 피부과, 안과, 이비인후과, 비뇨기과, 산부인과, 정신건강의학과, 신경과, 응급의학과, 치과, 기타
                    
                    ## 출력 형식(JSON)
                    {
                        "need_quit": True or False,
                        "department": "진료과 이름 (관련 없음이면 null)"
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
    need_quit = result.get("need_quit", False)
    
    if need_quit:
        final_answer = "죄송합니다. 조금 더 상세히 설명해주시면 도와드리도록 하겠습니다."    
    return {
        **state,
        "need_quit":need_quit,
        "department": result.get("department"),
        "final_answer": final_answer
    }
    
        
        
def classify_quit(state: GraphState) -> str:
    if state.get("need_quit", False):
        return END
    return "search_node"
