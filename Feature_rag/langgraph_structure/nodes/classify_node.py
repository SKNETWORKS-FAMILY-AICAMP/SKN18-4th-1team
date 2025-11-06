from langgraph_structure.init_state import GraphState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import HumanMessagePromptTemplate
from langgraph.graph import END
from langgraph_structure.utils import model

# 증상을 의미하는 질문인지, 쓸데없는 질문인지 판별하는 node
def classify_node(state: GraphState) -> GraphState:
    final_answer=""
    chat_prompt = ChatPromptTemplate(
        messages=[
            # system 역할
            SystemMessage(
                content=("""
                    당신은 의료전문가 입니다.
                    사용자가 입력한 질문이 병원증상과 관련된 질문인지 판단합니다.
                    증상과 관련이 있다면 'Yes'라고 대답하고, 그렇지 않으면 'No' 라고 대답합니다."""
                )
            ),
            # human 역할
            HumanMessagePromptTemplate.from_template("""
                {question}
            """),
        ]
    )
    llm = model(model_name='gpt-5-nano')
    chain = chat_prompt | llm | StrOutputParser()
    response = chain.invoke({'question': state.get('question')}).strip()
    need_quit = True if response == "No" else False
    
    if need_quit:
        final_answer = "죄송합니다. 조금 더 상세히 설명해주시면 도와드리도록 하겠습니다."    
    return {
        **state,
        "need_quit":need_quit,
        "final_answer": final_answer
    }
    
        
        
def classify_quit(state: GraphState) -> str:
    if state.get("need_quit", False):
        return END
    return "search_node"
