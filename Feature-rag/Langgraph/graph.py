from langgraph.graph import StateGraph, END
from init_state import GraphState
from .nodes.classify_node import classify_quit, classify_node

def create_graph_flow():
    """input: pdf인 경우의 그래프"""
    graph = StateGraph(GraphState)

    graph.add_node("classify_node", classify_node)
    graph.add_node("search_node", )
    graph.add_node("eval_node", )
    graph.add_node("evaluate_chunk_node", )
    graph.add_node("rewrite_question_node", )
    graph.add_node("generation_llm_node", )
    graph.add_conditional_edges(
    "classify_node",     # 출발 노드 이름
    classify_quit,   # 분기 조건 함수
    {
        END: END,   # 조건 결과 → 다음 노드
        "search_node": "search_node",
    }
    )
    
    
    graph.set_entry_point("classify_node")
    graph.add_edge("classify_node", "search_node")
    graph.add_edge("retrieve", "evaluate_chunk")
    graph.add_edge("evaluate_chunk", "generate_answer")
    graph.add_edge("generate_answer", END)

    return graph.compile()


