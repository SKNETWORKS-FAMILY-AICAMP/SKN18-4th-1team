from langchain_core.prompts import PromptTemplate
from langgraph_structure.init_state import GraphState
from langgraph_structure.utils import model

def __get_prompt_for_rewriting_question():
    template = """
        당신은 의료 RAG 검색을 위해 사용자의 질문을 **의학적 핵심 키워드로 정규화하는 전문가**입니다.
        사용자가 말한 일상 표현을 제거하고, 의학 문서 검색에 적합한 **증상 중심 키워드 리스트**로 재작성하세요.

        -------
        [현재 질문]
        {question}

        [이전 대화 요약(있다면 참고)]
        {summary}
        -------

        ## 재작성 규칙
        1. 사용자의 증상·신체 부위·불편감을 **의학적 표현의 핵심 키워드**로 정리합니다.
        2. 현재 질문에 증상 정보가 부족하면 이전 요약을 참고하여 증상·부위·중증도를 추출합니다.
        3. 병원 추천 문장처럼 구체적 요청만 있는 경우에도, 요약 속 증상 정보를 기반으로 키워드를 만들어야 합니다.
        4. 감탄사, 감정 표현, 일상적 부사·형용사는 모두 제거합니다.
        5. 출력은 **완전한 문장 대신 키워드 나열** 형식으로 표현하되, 최소 2개 이상의 키워드를 포함합니다.
        6. 반드시 **한국어**로 작성합니다.

        ## 출력 형식
        - "키워드1, 키워드2, 키워드3" 형식으로 출력하세요.
        """

    return PromptTemplate.from_template(template)

def question_retrive(state: GraphState) -> GraphState:
    """Rewrite the question for a better retrieval query."""

    llm = model("gpt-5-nano", temperature=0.3)
    chain = __get_prompt_for_rewriting_question() | llm

    result = chain.invoke(
        {
            "question": state.get("question", ""),
            "summary": state.get("summary", ""),
        }
    )
    return {
        **state,
        "rewrite_question": result.content,
    }
