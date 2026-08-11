"""Similarity search over a persisted FAISS index."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from ai_eng_assistant.config import get_settings
from ai_eng_assistant.ingest.indexer import load_index


def get_retriever(
    index_path: Path | str,
    *,
    k: int | None = None,
) -> VectorStoreRetriever:
    settings = get_settings()
    store = load_index(index_path)
    return store.as_retriever(search_kwargs={"k": k or settings.retrieval_k})


def retrieve_documents(
    question: str,
    index_path: Path | str,
    *,
    k: int | None = None,
) -> list[Document]:
    retriever = get_retriever(index_path, k=k)
    return list(retriever.invoke(question))
