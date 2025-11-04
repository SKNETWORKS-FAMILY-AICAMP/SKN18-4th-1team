# 증상을 의미하는 질문인지, 쓸데없는 질문인지 판별하는 node
from init_state import GraphState
from Langgraph.graph import END

def classify_node(state: GraphState) -> GraphState:
    return {
        **state
    }
    
        
        
def classify_quit(state: GraphState) -> str:
    if state.get("need_quit", False):
        return END
    return "search_node"
        