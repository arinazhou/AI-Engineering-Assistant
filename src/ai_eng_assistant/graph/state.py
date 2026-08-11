"""Graph state for the engineering assistant workflow."""

from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.documents import Document
from langgraph.graph.message import add_messages


class AssistantState(TypedDict, total=False):
    question: str
    context_docs: list[Document]
    answer: str
    sources: list[str]
    # Reserved for multi-turn chat extensions
    messages: Annotated[list, add_messages]
