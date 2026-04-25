"""LangGraph agent graph definition.

Builds a StateGraph that orchestrates the agent's reasoning loop:
    agent → (should_continue?) → tool_node → agent → ... → END
"""

from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.nodes import agent_node
from app.agent.state import AgentState
from app.tools.bigquery_tools import ALL_TOOLS

logger = logging.getLogger(__name__)


def _should_continue(state: AgentState) -> str:
    """Routing function: check if the last message has tool calls.

    Returns:
        "tools" if the LLM wants to call a tool.
        "end" if the LLM generated a final response.
    """
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        logger.info(
            "Agent decided to call tools: %s",
            [tc["name"] for tc in last_message.tool_calls],
        )
        return "tools"

    return "end"


def build_graph() -> StateGraph:
    """Construct and compile the agent graph.

    Flow:
        START → agent → should_continue?
            → "tools" → tool_node → agent (loop)
            → "end"  → END
    """
    tool_node_instance = ToolNode(ALL_TOOLS)

    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node_instance)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        _should_continue,
        {
            "tools": "tools",
            "end": END,
        },
    )

    graph.add_edge("tools", "agent")

    compiled = graph.compile()
    logger.info("Agent graph compiled successfully.")
    return compiled
