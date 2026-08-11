"""CLI for indexing repositories and asking engineering questions."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from ai_eng_assistant.config import DEFAULT_SAMPLE_REPO, get_settings, index_dir_for
from ai_eng_assistant.graph.workflow import ask
from ai_eng_assistant.ingest.indexer import build_index

app = typer.Typer(
    name="ai-eng",
    help="AI Engineering Assistant — RAG over software repositories.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def _require_api_key() -> None:
    if not get_settings().openai_api_key:
        console.print(
            "[red]OPENAI_API_KEY is missing.[/red] "
            "Copy [bold].env.example[/bold] to [bold].env[/bold] and add your key."
        )
        raise typer.Exit(code=1)


@app.command("index")
def index_cmd(
    path: Path = typer.Option(
        DEFAULT_SAMPLE_REPO,
        "--path",
        "-p",
        help="Repository path to index.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Optional index name (defaults to directory name).",
    ),
) -> None:
    """Index a repository into a local FAISS store."""
    _require_api_key()
    console.print(f"Indexing [cyan]{path.resolve()}[/cyan] ...")
    out = build_index(path, index_name=name)
    console.print(Panel.fit(f"Index saved to [green]{out}[/green]", title="Done"))


@app.command("ask")
def ask_cmd(
    question: str = typer.Argument(..., help="Engineering / debugging question."),
    index: Optional[Path] = typer.Option(
        None,
        "--index",
        "-i",
        help="Path to a FAISS index directory.",
    ),
    repo: Path = typer.Option(
        DEFAULT_SAMPLE_REPO,
        "--repo",
        "-r",
        help="Repo whose default index name to use when --index is omitted.",
    ),
    k: Optional[int] = typer.Option(
        None,
        "--k",
        help="Number of chunks to retrieve.",
    ),
) -> None:
    """Ask a question over an indexed repository."""
    _require_api_key()
    index_path = index or index_dir_for(repo)
    if not index_path.exists():
        console.print(
            f"[red]Index not found:[/red] {index_path}\n"
            f"Run: [bold]python -m ai_eng_assistant.cli index --path {repo}[/bold]"
        )
        raise typer.Exit(code=1)

    console.print(f"Using index [cyan]{index_path}[/cyan]")
    result = ask(question, index_path, k=k)
    console.print(Panel(Markdown(result["answer"]), title="Answer", border_style="green"))
    if result["sources"]:
        console.print("Sources:")
        for src in result["sources"]:
            console.print(f"  • {src}")


@app.command("chat")
def chat_cmd(
    index: Optional[Path] = typer.Option(
        None,
        "--index",
        "-i",
        help="Path to a FAISS index directory.",
    ),
    repo: Path = typer.Option(
        DEFAULT_SAMPLE_REPO,
        "--repo",
        "-r",
        help="Repo whose default index name to use when --index is omitted.",
    ),
) -> None:
    """Interactive Q&A loop over an indexed repository."""
    _require_api_key()
    index_path = index or index_dir_for(repo)
    if not index_path.exists():
        console.print(
            f"[red]Index not found:[/red] {index_path}\n"
            f"Run: [bold]python -m ai_eng_assistant.cli index --path {repo}[/bold]"
        )
        raise typer.Exit(code=1)

    console.print(
        Panel.fit(
            f"Chat mode — index [cyan]{index_path}[/cyan]\n"
            "Type a question, or [bold]exit[/bold] / [bold]quit[/bold] to leave.",
            title="AI Engineering Assistant",
        )
    )
    while True:
        try:
            question = console.input("[bold blue]You>[/bold blue] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nBye.")
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            console.print("Bye.")
            break
        result = ask(question, index_path)
        console.print(Panel(Markdown(result["answer"]), title="Assistant", border_style="green"))
        if result["sources"]:
            console.print("Sources: " + ", ".join(result["sources"]))


@app.callback()
def main() -> None:
    """AI Engineering Assistant CLI."""


if __name__ == "__main__":
    app()
