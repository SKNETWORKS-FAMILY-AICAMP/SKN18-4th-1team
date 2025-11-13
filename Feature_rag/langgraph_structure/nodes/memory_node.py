# env 로드
from dotenv import load_dotenv
import os

# 스크립트 실행 위치 기준 두 단계 상위 폴더
root_path = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
load_dotenv(os.path.join(root_path, ".env"))

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from typing import Any, Dict, List
from langgraph_structure.init_state import GraphState

from sqlalchemy import create_engine, text
from sqlalchemy import create_engine
import json

engine = create_engine(os.getenv("CONNECTION_STRING"))

def memory_node_to_db(state: GraphState) -> GraphState:
    """
    검색 결과와 LLM 응답을 PostgreSQL(DB)에 그대로 저장
    """
    search_results = state.get("hospitals", [])
    llm_response = state.get("llm_answer", "")

    # JSON 형태로 직렬화
    search_results_json = json.dumps(search_results, ensure_ascii=False)

    # 테이블 생성 (없으면)
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS memory (
            id SERIAL PRIMARY KEY,
            search_results JSONB,
            llm_response TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
        """))

        # 데이터 삽입
        conn.execute(
            text("""
            INSERT INTO memory (search_results, llm_response)
            VALUES (:search_results, :llm_response)
            """),
            {"search_results": search_results_json, "llm_response": llm_response}
        )

    return state