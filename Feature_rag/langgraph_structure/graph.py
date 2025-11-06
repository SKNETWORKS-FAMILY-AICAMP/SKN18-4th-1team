from langgraph.graph import StateGraph, END
from langgraph_structure.init_state import GraphState
from langgraph_structure.nodes.classify_node import classify_quit, classify_node
from langgraph_structure.nodes.eval_node import evaluate_chunk_node,classify_retrieval
from langgraph_structure.nodes.rewrite_question import question_retrive
from langgraph_structure.nodes.generation_llm import generation_llm_node
from langgraph_structure.nodes.search_hospital import search_hospital_node
from langgraph_structure.nodes.search_vectordb import search_node


def create_graph_flow():
    # 사용할 변수 정의
    graph = StateGraph(GraphState)

    # 노드 선언
    graph.add_node("classify_node", classify_node)
    graph.add_node("search_node", search_node )
    graph.add_node("evaluate_chunk_node", evaluate_chunk_node )
    graph.add_node("rewrite_question_node",question_retrive )
    graph.add_node("generation_llm_node",generation_llm_node )
    graph.add_node("search_hospital_node",search_hospital_node)
    
    # 엣지 선언 
    graph.set_entry_point("classify_node")
    graph.add_conditional_edges(
    "classify_node",     # 출발 노드 이름
    classify_quit,   # 분기 조건 함수
    {
        END: END,   # 조건 결과 → 다음 노드
        "search_node": "search_node",
    })
    graph.add_edge("search_node", "evaluate_chunk_node")
    graph.add_conditional_edges(
        "evaluate_chunk_node",
        classify_retrieval,
        {
            END : END,
            "rewrite_question_node":"rewrite_question_node",
            "search_hospital_node":"search_hospital_node"
                
        }
    )
    graph.add_edge("rewrite_question_node", "classify_node")
    graph.add_edge("search_hospital_node", "generation_llm_node")
    graph.add_edge("generation_llm_node", END)

    return graph.compile()


graph = create_graph_flow()

