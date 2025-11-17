from langgraph_structure.init_state import GraphState
from tavily import TavilyClient
from langgraph.graph import END
import os
from dotenv import load_dotenv

load_dotenv()


def web_search_node(state: GraphState) -> GraphState:
    final_answer = ""
    combined_metadata = []
    relevant_contents = []
    scores = []

    client = TavilyClient(os.getenv("TAVILY_API_KEY"))
    response = client.search(
        max_results=3,
        query=state.get("rewrite_question", ""),
        include_domains=[
            "https://www.snuh.org",
            "https://health.kdca.go.kr",
            "https://www.amc.seoul.kr",
        ],
    )
    check_quit = not bool(response["results"])
    if not check_quit:
        combined_metadata = [
            f"{item['title']} \n- {item['url']}" for item in response["results"]
        ]
        scores = [item.get("score") for item in response["results"]]
        relevant_contents = [item.get("content") for item in response["results"]]
    else:
        final_answer = "죄송합니다. 해당 질문의 답을 찾을 수 없습니다.!"

    mean_score = sum(scores) / len(scores) if scores else 0.0

    return {
        "check_quit": check_quit,
        "relevant_contents": relevant_contents,
        "web_mean_score": mean_score,
        "relevant_source": combined_metadata,
        "final_answer": final_answer,
    }


def check_quit(state: GraphState) -> str:
    if state["check_quit"]:
        return END

    service = state.get("service")
    if service == "hospital":
        return "judgment_symtom_node"
    return "generation_llm_node"
    
