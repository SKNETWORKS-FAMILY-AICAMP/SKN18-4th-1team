"""
증상 분석 서비스 로직
"""
from typing import Optional
import logging
from mediscope.langgraph_structure.graph import create_graph_flow
from mediscope.langgraph_structure.nodes.memory_node import (
    memory_update_node as run_memory_update_node,
)

DEFAULT_FALLBACK_MESSAGE = (
    "죄송합니다. 답변을 생성하지 못했습니다. 증상을 조금 더 자세히 알려주시면 도와드릴 수 있어요."
)

logger = logging.getLogger(__name__)
langgraph_app = create_graph_flow()


def analyze_symptoms(
    symptoms_text,
    *,
    memory_summary: Optional[str] = None,
    region: Optional[str] = None,
    survey_summary: Optional[str] = None,
) -> dict:
    """
    LangGraph에 질문을 전달하고, 생성된 상태를 반환합니다.
    memory_summary가 주어지면 그래프 초기 상태에 그대로 전달합니다.
    """

    input_data = {"question": symptoms_text}
    if memory_summary:
        input_data["summary"] = memory_summary
    if region:
        input_data["region"] = region
    if survey_summary:
        input_data["survey_result"] = survey_summary

    response_state = langgraph_app.invoke(input_data)

    final_answer_text = response_state.get("final_answer")
    if not final_answer_text:
        final_answer_text = DEFAULT_FALLBACK_MESSAGE
        response_state["final_answer"] = final_answer_text

    summary_seed = response_state.get("summary") or memory_summary or ""
    should_generate_summary = final_answer_text != DEFAULT_FALLBACK_MESSAGE
    if should_generate_summary:
        # 항상 메모리를 새로 갱신하여 Django 측에서도 요약을 확보한다.
        try:
            updated_state = run_memory_update_node(
                {
                    "summary": summary_seed,
                    "question": symptoms_text,
                    "final_answer": final_answer_text,
                }
            )
            new_summary = updated_state.get("summary")
            if new_summary:
                response_state["summary"] = new_summary
                logger.info("[chat] summary refreshed (len=%s)", len(new_summary))
        except Exception as exc:
            logger.warning("[chat] summary generation failed: %s", exc)

    return response_state
