import os
from dotenv import load_dotenv
from langgraph_structure.init_state import GraphState
from memory_node import memory_node_to_db  # memory_node 파일명에 맞게 수정

# .env 로드 (CONNECTION_STRING 불러오기)
load_dotenv()

# 테스트용 더미 데이터
state: GraphState = {
    "hospitals": [
        {"name": "서울중앙병원", "department": "내과"},
        {"name": "한빛의원", "department": "소아과"}
    ],
    "llm_answer": "서울 지역 내과 병원으로 서울중앙병원을 추천합니다."
}

# 노드 실행
new_state = memory_node_to_db(state)

print("✅ memory_node 실행 완료")
print("state 내용:", new_state)
