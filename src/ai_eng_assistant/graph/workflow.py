"""Compile and run the LangGraph retrieve → generate workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph

from ai_eng_assistant.graph.nodes import generate, make_retrieve_node
from ai_eng_assistant.graph.state import AssistantState


def build_graph(index_path: Path | str, *, k: int | None = None):
    """Build a compiled LangGraph app bound to an index."""
    graph = StateGraph(AssistantState)
    graph.add_node("retrieve", make_retrieve_node(index_path, k=k))
    graph.add_node("generate", generate)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()


def ask(
    question: str,
    index_path: Path | str,
    *,
    k: int | None = None,
) -> dict[str, Any]:
    """Run the assistant graph and return answer + sources + docs."""
    app = build_graph(index_path, k=k)
    result = app.invoke({"question": question})
    return {
        "question": question,
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "context_docs": result.get("context_docs", []),
    }
