"""LangGraph node functions for the media analyst agent.

Nodes:
    agent_node: Invokes the LLM with available tools bound.
    tool_node: Executes the tool selected by the LLM.
"""

from __future__ import annotations

import logging

from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.agent.prompts import build_system_prompt
from app.agent.state import AgentState
from app.config import settings
from app.tools.bigquery_tools import ALL_TOOLS

logger = logging.getLogger(__name__)


def _get_llm() -> ChatGoogleGenerativeAI:
    """Build the Gemini LLM instance with tools bound."""
    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        api_key=settings.gemini_api_key,
        temperature=0,
        retries=2,
    )
    return llm.bind_tools(ALL_TOOLS)


def agent_node(state: AgentState) -> dict:
    """Invoke the LLM to reason about the user's question.

    The LLM decides whether to call a tool or respond directly.
    """
    llm = _get_llm()

    messages = state["messages"]

    has_system = any(isinstance(m, SystemMessage) for m in messages)
    if not has_system:
        messages = [SystemMessage(content=build_system_prompt())] + list(messages)

    try:
        response = llm.invoke(messages)
        logger.info("LLM response type: %s", type(response).__name__)
        return {"messages": [response]}
    except Exception as exc:
        logger.error("LLM invocation failed: %s", exc)
        raise RuntimeError(f"Erro ao invocar LLM: {exc}") from exc
