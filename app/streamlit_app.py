"""Streamlit UI for the AI Engineering Assistant."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Ensure `src/` is on the path when launched via `streamlit run`
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_eng_assistant.config import (  # noqa: E402
    DEFAULT_SAMPLE_REPO,
    get_settings,
    index_dir_for,
)
from ai_eng_assistant.graph.workflow import ask  # noqa: E402
from ai_eng_assistant.ingest.indexer import build_index  # noqa: E402

st.set_page_config(
    page_title="AI Engineering Assistant",
    layout="wide",
)

st.title("AI Engineering Assistant")
st.caption("RAG over software repositories — LangGraph · LangChain · FAISS · OpenAI")


def _api_key_present() -> bool:
    return bool(get_settings().openai_api_key)


with st.sidebar:
    st.header("Setup")
    if _api_key_present():
        st.success("OPENAI_API_KEY is set")
    else:
        st.error("OPENAI_API_KEY missing — add it to `.env`")

    st.subheader("Index")
    repo_path = st.text_input(
        "Repository path to index",
        value=str(DEFAULT_SAMPLE_REPO),
    )
    index_name = st.text_input("Index name (optional)", value="")
    if st.button("Build / rebuild index", type="primary", disabled=not _api_key_present()):
        with st.spinner("Indexing repository..."):
            try:
                out = build_index(
                    repo_path,
                    index_name=index_name or None,
                )
                st.session_state["index_path"] = str(out)
                st.success(f"Index saved to {out}")
            except Exception as exc:  # noqa: BLE001 — show in UI
                st.error(str(exc))

    default_index = st.session_state.get(
        "index_path",
        str(index_dir_for(Path(repo_path), index_name or None)),
    )
    index_path = st.text_input("Index directory", value=default_index)
    k = st.slider("Top-k chunks", min_value=1, max_value=12, value=5)

st.subheader("Ask a question")
question = st.text_area(
    "Question",
    placeholder="Why does the last page of orders come back empty?",
    height=100,
)

col1, col2 = st.columns([1, 4])
with col1:
    run = st.button("Ask", type="primary", disabled=not _api_key_present())

if run:
    if not question.strip():
        st.warning("Enter a question first.")
    elif not Path(index_path).exists():
        st.warning("Index not found. Build an index from the sidebar first.")
    else:
        with st.spinner("Retrieving context and generating answer..."):
            try:
                result = ask(question.strip(), index_path, k=k)
                st.markdown("### Answer")
                st.markdown(result["answer"])
                if result["sources"]:
                    st.markdown("### Sources")
                    for src in result["sources"]:
                        st.markdown(f"- `{src}`")
                with st.expander("Retrieved chunks"):
                    for i, doc in enumerate(result["context_docs"], start=1):
                        src = doc.metadata.get("source", "unknown")
                        st.markdown(f"**[{i}] `{src}`**")
                        st.code(doc.page_content[:2000], language="python")
            except Exception as exc:  # noqa: BLE001 — show in UI
                st.error(str(exc))

st.divider()
st.markdown(
    "**Example questions:** Why does pagination return empty? · "
    "Why does auth always succeed? · Why do failed orders return ok? · "
    "Why is the charged total a few cents low?"
)
