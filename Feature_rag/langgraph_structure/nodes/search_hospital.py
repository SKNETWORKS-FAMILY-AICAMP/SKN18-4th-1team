import sqlite3
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

def search_hospital_node():
    """
    사용자의 질문을 분석하여 DB 검색에 사용할 키워드를 생성하는 노드
    """
    template = """
    당신은 의료 안내 시스템의 전문가입니다.
    아래 사용자의 질문을 분석하여 병원 데이터베이스 검색에 사용할 핵심 키워드를 만드세요.
    예: "정형외과", "피부과", "내과", "응급실", "소아청소년과" 등

    질문: {question}

    출력은 키워드 하나만 주세요.
    """
    return PromptTemplate.from_template(template)


def search_hospital(state: dict) -> dict:
    """
    병원 RDB에서 관련 병원 정보를 검색하는 노드
    """
    model = ChatOpenAI(
        model="gpt-5-nano", 
        reasoning_effort="low"
        )
    chain = search_hospital_node() | model

    question = state.get("question", "")
    response = chain.invoke({"question": question})
    keyword = response.content.strip()

    # DB 연결 (SQLite 예시)
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    # SQL 실행 (부분 일치 검색)
    query = """
    SELECT name, addr, special_field, nursing_grade, medical_info
    FROM hospitals
    WHERE special_field LIKE ? OR name LIKE ?;
    """
    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
    results = cursor.fetchall()
    conn.close()

    # 결과 문자열 정리
    formatted = "\n\n".join([
        f"병원명: {r[0]}\n주소: {r[1]}\n전문분야: {r[2]}\n간호등급: {r[3]}"
        for r in results
    ])

    return {
        **state,
        "search_keyword": keyword,
        "hospital_results": formatted,
        "route": "output"
    }
