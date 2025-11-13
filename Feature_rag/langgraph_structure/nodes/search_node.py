from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import set_embedding_model
from langgraph_structure.Rag.custom_pgvector import CustomPGVector


def search_vectordb(state: GraphState) -> GraphState:
    """질문과 관련된 증상 chunk 가져오는 노드"""
    # 사용 변수
    search_chunks=[]
    mean_similarity_score = 0.0
    embed = set_embedding_model()
    vectorstore = CustomPGVector(embedding_fn=embed)
    question = state.get("question","") # 추후 수정필요
    filter = state.get("department", [])
    if not filter or all(d == "기타" for d in filter):
        results = vectorstore.similarity_search_with_score(question, k=5)
    else:
        results = vectorstore.similarity_search_with_score(question, k=5, filter=filter)
    
    if results:
        for doc, score in results:
            search_chunks.append(doc)
            mean_similarity_score+=score
        mean_similarity_score/=5
    

    return {
        **state,
        "mean_similarity_score": mean_similarity_score,
        "search_chunks":search_chunks
    }
