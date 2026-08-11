"""Load source files from a repository into LangChain Documents."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document

INCLUDE_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
}

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    "data",
    ".idea",
    ".vscode",
}


def _should_skip_dir(name: str) -> bool:
    return name in SKIP_DIR_NAMES or name.startswith(".")


def load_repo_documents(repo_path: Path | str) -> list[Document]:
    """Walk a repo and return one Document per eligible file."""
    root = Path(repo_path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")

    documents: list[Document] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(_should_skip_dir(part) for part in path.relative_to(root).parts[:-1]):
            continue
        if path.suffix.lower() not in INCLUDE_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if not text.strip():
            continue

        rel = str(path.relative_to(root))
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": rel,
                    "path": str(path),
                    "repo_root": str(root),
                },
            )
        )
    return documents
