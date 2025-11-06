# vectordb 검색
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from Langgraph.init_state import GraphState

def search_node(state: GraphState) -> GraphState:
    return state