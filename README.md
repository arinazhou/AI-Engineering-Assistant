# AI Engineering Assistant

LLM-powered engineering assistant that answers questions over software repositories using **LangGraph**, **LangChain**, **FAISS**, and the **OpenAI API**.

It indexes source code, retrieves relevant context (RAG), and generates debugging recommendations with file citations.

## Architecture

```text
Repo files → Loader → Chunker → OpenAI embeddings → FAISS
                                              ↓
User question → LangGraph (retrieve → generate) → Answer + citations
```

- **Ingest:** walk a repo, chunk code/docs, embed, persist a local FAISS index
- **Ask:** LangGraph workflow retrieves top-k chunks, then prompts OpenAI with modular system/RAG templates
- **Interfaces:** Typer CLI + Streamlit UI (same core APIs)

## Quick start

### 1. Setup

```bash
cd AI-Engineering-Assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
```

### 2. Index the bundled sample repo

```bash
python -m ai_eng_assistant.cli index --path sample_repo
```

Index is written to `data/indexes/sample_repo/`.

### 3. Ask via CLI

```bash
python -m ai_eng_assistant.cli ask "Why does the last page of orders come back empty?"
python -m ai_eng_assistant.cli chat
```

### 4. Streamlit UI

```bash
streamlit run app/streamlit_app.py
```

## Example questions (sample_repo)

The bundled [`sample_repo/`](sample_repo/) is a tiny order service with intentional bugs:

- Why does the last page of orders come back empty?
- Why does authentication always succeed even with a bad token?
- Why do failed orders still return success?
- Why is the charged total sometimes a few cents low?

## Project layout

```text
sample_repo/                 # demo codebase with intentional bugs
src/ai_eng_assistant/
  ingest/                    # loader, chunker, FAISS indexer
  retrieval/                 # similarity search
  graph/                     # LangGraph state, nodes, workflow
  prompts.py                 # modular system + RAG prompts
  cli.py                     # index | ask | chat
app/streamlit_app.py         # thin UI over the same APIs
data/indexes/                # persisted FAISS indexes (gitignored)
```

## Design notes

- **RAG** keeps answers grounded in the actual repository instead of model memory.
- **LangGraph** separates retrieve vs generate as modular nodes so you can later add critique, re-retrieve, or tool-calling steps without rewriting the pipeline.
- **FAISS** gives local, fast semantic code search with no external vector DB.
- **CLI + Streamlit** share one core so demos and scripting stay in sync.

## Requirements

- Python 3.11+
- OpenAI API key (`gpt-4o-mini` + `text-embedding-3-small` by default)
