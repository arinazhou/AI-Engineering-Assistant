"""Build and persist FAISS indexes over repository chunks."""

from __future__ import annotations

import json
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from ai_eng_assistant.config import get_settings, index_dir_for
from ai_eng_assistant.ingest.chunker import chunk_documents
from ai_eng_assistant.ingest.loader import load_repo_documents


def _embeddings() -> OpenAIEmbeddings:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )


def build_index(
    repo_path: Path | str,
    *,
    index_name: str | None = None,
    persist_dir: Path | str | None = None,
) -> Path:
    """Load, chunk, embed, and save a FAISS index for a repository.

    Returns the directory where the index was written.
    """
    root = Path(repo_path).resolve()
    out = Path(persist_dir) if persist_dir else index_dir_for(root, index_name)
    out.mkdir(parents=True, exist_ok=True)

    documents = load_repo_documents(root)
    if not documents:
        raise ValueError(f"No indexable files found under {root}")

    chunks = chunk_documents(documents)
    if not chunks:
        raise ValueError(f"No chunks produced from {root}")

    store = FAISS.from_documents(chunks, _embeddings())
    store.save_local(str(out))

    meta = {
        "repo_path": str(root),
        "num_files": len(documents),
        "num_chunks": len(chunks),
        "embedding_model": get_settings().embedding_model,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return out


def load_index(index_path: Path | str) -> FAISS:
    """Load a previously saved FAISS index from disk."""
    path = Path(index_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Index directory not found: {path}")
    return FAISS.load_local(
        str(path),
        _embeddings(),
        allow_dangerous_deserialization=True,
    )
