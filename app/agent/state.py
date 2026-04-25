"""Typed state definition for the LangGraph agent."""

from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State that flows through the LangGraph agent nodes.

    Attributes:
        messages: Conversation history with automatic message merging.
    """

    messages: Annotated[list[BaseMessage], add_messages]
