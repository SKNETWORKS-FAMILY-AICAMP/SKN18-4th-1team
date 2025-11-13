from langchain_core.prompts import PromptTemplate
from langgraph_structure.init_state import GraphState
from langgraph.graph import END
from langgraph_structure.utils import model
import json

def evaluate_chunk_node(state: GraphState) -> GraphState:
    """데이터베이스에서 추출한 chunk가 질문과 연관되어있는지 평가하는 함수"""
    
    # 사용할 변수 초기값 정의
    final_answer=""
    relevant_contents: list[str] = []
    relevant_category: list[str] = []
    relevance_scores: list[float] = []
    feedback_messages: list[str] = []
    relevant_source: list[str] = []
    
    relevance_prompt = PromptTemplate.from_template(
        '''
        # **검색 문서 관련성 평가**
        
        당신은 **의료 전문 어시스턴트** 입니다.
        아래에 주어진 '질문'과 '문서'를 보고, 문서가 질문에 얼마나 관련 있는지를 판단해라.
        
        ## 출력 형식 (JSON)
        {{
            "evaluation_score": (0~100),
            "evaluation_detail": "간단한 이유 설명"
        }}
        ---
        # 질문:
        {question}

        # 문서:
        {chunk}
        '''
    )
    llm = model("gpt-4o-mini", temperature=0.0)
    chain = relevance_prompt | llm
    for doc in state.get("search_chunks"):
        chunk = doc.page_content
        response = chain.invoke(
            {'question':state.get("question"), "chunk": chunk}
        )
        result = json.loads(response.content)
        score = result.get("evaluation_score", 0)
        if score >= 60:
            relevant_category.append(doc.metadata["domain"])
            relevant_source.append(doc.metadata['source_spec'])
            relevant_contents.append(chunk)
            relevance_scores.append(score)
        else:
            detail = result.get("evaluation_detail")
            if detail:
                feedback_messages.append(detail)
        
    retrieval_question = not bool(relevant_contents)
        
    if retrieval_question and state.get("max_token"):
        final_answer = "죄송합니다. 조금 더 상세히 설명해주시면 도와드리도록 하겠습니다."
        
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        
    return {
        **state,
        "relevant_source":relevant_source,
        "relevant_category":relevant_category,
        "relevant_contents": relevant_contents,
        "retrieval_question": retrieval_question,
        "avg_relevance": avg_relevance,
        "feedback_messages": "\n".join(feedback_messages),
        "final_answer": final_answer
    }
    
def classify_retrieval(state: GraphState) -> str:
    if state["retrieval_question"]:
        if state.get("max_token"):
            return END  
        return "rewrite_question_node"
    # 2) service 종류에 따라 라우팅
    service = state.get("service")
    if service == "symptom":
        return "generation_llm_node"
    elif service == "hospital":
        return "judgment_symtom_node"

