"""Prompt templates for repository Q&A."""

from __future__ import annotations

SYSTEM_PROMPT = """You are an expert software engineering assistant.
You answer questions about a codebase using only the retrieved source context.
Be concrete: name files, functions, and likely root causes.
When suggesting fixes, show a short corrected snippet when helpful.
If the context is insufficient, say what is missing instead of inventing code.
Always cite source file paths from the context metadata."""

RAG_USER_TEMPLATE = """Question:
{question}

Retrieved context (each block starts with its source path):
{context}

Write a clear debugging-oriented answer with citations like `path/to/file.py`."""


def format_context(docs: list) -> str:
    """Format retrieved documents for the prompt."""
    blocks: list[str] = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "unknown")
        blocks.append(f"[{i}] source: {source}\n{doc.page_content}")
    return "\n\n---\n\n".join(blocks) if blocks else "(no context retrieved)"
