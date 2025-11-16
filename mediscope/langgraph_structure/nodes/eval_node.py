from langchain_core.prompts import PromptTemplate
from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import model
import json
def evaluate_chunk_node(state: GraphState) -> GraphState:
    """데이터베이스에서 추출한 chunk가 질문과 연관되어있는지 평가하는 함수"""
    
    # 사용할 변수 초기값 정의
    final_answer=""
    relevant_contents: list[str] = []
    relevant_category: list[str] = []
    relevance_scores: list[float] = []
    relevant_source= []
    
    relevance_prompt = PromptTemplate.from_template(
        '''
        # **검색 문서 관련성 평가**
        
        당신은 **의료 전문 어시스턴트** 입니다.
        아래에 주어진 '질문'과 '문서'를 보고, 문서가 질문에 얼마나 관련 있는지를 판단해라.
        
        ## 출력 형식 (JSON 형태로 !!)
        {{
            "evaluation_score": (0~100)
        }}
        ---
        # 질문:
        {question}

        # 문서:
        {chunk}
        '''
    )
    llm = model("gpt-5-nano", temperature=0.0)
    chain = relevance_prompt | llm
    for doc in state.get("search_chunks"):
        chunk = doc.page_content
        response = chain.invoke(
            {'question':state.get("question"), "chunk": chunk}
        )
        result = json.loads(response.content)
        score = result.get("evaluation_score", 0)
        if score >= 50:
            relevant_category.append(doc.metadata["domain"])
            relevant_source.append(doc.metadata['source_spec'])
            relevant_contents.append(chunk)
            relevance_scores.append(score)
            
    check_web = not bool(relevant_contents)
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        
    return {
        **state,
        "relevant_source":relevant_source,
        "relevant_category":relevant_category,
        "relevant_contents": relevant_contents,
        "check_web": check_web,
        "avg_relevance": avg_relevance,
        "final_answer": final_answer
    }
    
def classify_retrieval(state: GraphState) -> str:
    if state["check_web"]:
        return "web_search_node"
    
    # 2) service 종류에 따라 라우팅
    service = state.get("service")
    if service == "symptom":
        return "generation_llm_node"
    elif service == "hospital":
        return "judgment_symtom_node"

