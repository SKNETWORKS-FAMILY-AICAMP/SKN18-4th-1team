from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph_structure.init_state import GraphState


class summary_memory:
    """
    llm의 출력결과를 정리해서 기억하는 클래스입니다.
    """

    def __init__(self, max_messages: int = 4, model_name: str = "gpt-5-nano"):
        self.max_messages = max_messages
        self.llm = ChatOpenAI(model=model_name)
        print("summary_memory 준비 완료!")

    ############################################################
    # 오래된 메시지 요약
    ############################################################
    def summarize_old_messages(self, messages):
        if len(messages) <= self.max_messages:
            return messages
        
        old_messages = messages[:-self.max_messages]
        recent_messages = messages[-self.max_messages:]

        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 대화 내용을 간결하게 요약하는 전문가입니다.
                다음 대화를 3~5문장으로 압축하세요."""),
            ("user","다음 대화를 요약해주세요:\n\n{conversation}")
        ])

        conversation_text = ""
        for msg in old_messages:
            if msg.type == "human":
                conversation_text += f"사용자: {msg.content}\n"
            elif msg.type == "ai":
                conversation_text += f"AI: {msg.content}\n"

        try:
            summary_chain = summary_prompt | self.llm
            resp = summary_chain.invoke({"conversation": conversation_text})
            summary_content = resp.content
        except:
            summary_content = conversation_text[:400] + "..."

        summary_message = SystemMessage(
            content=f"[이전 대화 요약]\n{summary_content}"
        )

        return [summary_message] + recent_messages

    ############################################################
    # LangGraph 노드 정의
    ############################################################
    def chat_node_with_summary(self, state: MessagesState):
        summarized = self.summarize_old_messages(state["messages"])
        response = self.llm.invoke(summarized)
        return {"messages": [response]}


# 모듈 전역 인스턴스: 그래프 노드에서 재사용
_SUMMARY_HELPER = summary_memory()


def summary_memory_node(state: GraphState) -> GraphState:
    """
    Capture the latest Q/A from the pipeline and store it as conversation
    history with summarization. Intended to be placed after `generation_llm_node`.

    Input (from state):
    - question: str            # 사용자 질문
    - final_answer: str        # generation_llm_node가 생성한 답변
    - conversation_history: Optional[List[BaseMessage]]  # 누적 대화 (옵션)

    Output (to state):
    - conversation_history: List[BaseMessage]  # 요약 포함 최신 히스토리
    """

    # 기존 히스토리 불러오기 (없으면 빈 리스트)
    history = state.get("conversation_history", []) or []

    # 현재 턴의 Q/A 추가
    question = state.get("question", "") or ""
    final_answer = state.get("final_answer", "") or ""

    if question:
        history.append(HumanMessage(content=question))
    if final_answer:
        history.append(AIMessage(content=final_answer))

    # 오래된 메시지를 요약하여 용량 관리
    summarized_history = _SUMMARY_HELPER.summarize_old_messages(history)

    # 상태에 다시 저장하여 이후 턴에서 활용 가능
    return {
        **state,
        "conversation_history": summarized_history,
    }
