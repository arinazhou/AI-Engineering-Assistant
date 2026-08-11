"""LangGraph nodes: retrieve context and generate an answer."""

from __future__ import annotations

from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ai_eng_assistant.config import get_settings
from ai_eng_assistant.graph.state import AssistantState
from ai_eng_assistant.prompts import RAG_USER_TEMPLATE, SYSTEM_PROMPT, format_context
from ai_eng_assistant.retrieval.retriever import retrieve_documents


def make_retrieve_node(index_path: Path | str, *, k: int | None = None):
    """Factory for a retrieve node bound to a FAISS index directory."""

    def retrieve(state: AssistantState) -> AssistantState:
        question = state["question"]
        docs = retrieve_documents(question, index_path, k=k)
        sources = []
        for doc in docs:
            src = doc.metadata.get("source")
            if src and src not in sources:
                sources.append(src)
        return {
            "context_docs": docs,
            "sources": sources,
        }

    return retrieve


def generate(state: AssistantState) -> AssistantState:
    """Generate an answer from retrieved context using OpenAI chat."""
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )
    docs = state.get("context_docs") or []
    user_prompt = RAG_USER_TEMPLATE.format(
        question=state["question"],
        context=format_context(docs),
    )
    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )
    answer = response.content if isinstance(response.content, str) else str(response.content)
    return {"answer": answer}
