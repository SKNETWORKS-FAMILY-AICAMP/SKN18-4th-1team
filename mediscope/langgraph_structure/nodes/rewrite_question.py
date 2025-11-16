from langchain_core.prompts import PromptTemplate
from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import model

def __get_prompt_for_rewriting_question():
    template = """
        당신은 의료 RAG 검색을 위해 사용자의 질문을 **의학적 핵심 키워드로 정규화하는 전문가**입니다.  
        사용자가 말한 일상 표현을 제거하고, 의학 문서 검색에 적합한 **증상 중심 키워드 리스트**로 재작성하세요.

        -------
        [원본 질문]
        {question}
        -------

        ## 재작성 규칙
        1. 사용자의 증상·신체 부위·불편감을 **의학적 표현의 핵심 키워드**로만 정리합니다.
        예: “머리가 띵해요” → “두통, 어지러움”
        2. **병원 선택/병원 추천/어디로 가야하는지 묻는 문장은 모두 제거합니다.**
        예: “어느 병원 가야 하나요?” → 제거
        3. 필요하다면 **의학적으로 타당한 관련 키워드**를 추가할 수 있습니다.
        예: 설사 → “설사, 복통, 장염 가능성”
        4. 감탄사, 감정 표현, 일상적 부사·형용사는 모두 제거합니다.
        5. 출력은 **완전한 문장이 아니라 키워드 나열 형식**으로 표현합니다.
        6. 반드시 **한국어**로 작성합니다.

        ## 출력 형식
        - "키워드1, 키워드2, 키워드3" 형식으로 출력하세요.
        """

    return PromptTemplate.from_template(template)

def question_retrive(state: GraphState) -> GraphState:
    """Rewrite the question for a better retrieval query."""
    
    llm = model("gpt-5-nano",temperature=0.3)
    chain = __get_prompt_for_rewriting_question() | llm
    
    result = chain.invoke({
        "question": state["question"]
    })
    return {
        **state,
        "rewrite_question": result.content,
    }
