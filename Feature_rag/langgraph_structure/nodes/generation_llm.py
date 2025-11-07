from langgraph_structure.init_state import GraphState

def generation_llm_node(state: GraphState) -> GraphState:
    return {
        **state
    }
