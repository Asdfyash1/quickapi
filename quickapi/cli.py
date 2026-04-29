"""CLI entry point for QuickAPI."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from .scaffold import ProjectConfig, scaffold_project

console = Console()


@click.group()
@click.version_option(package_name="quickapi")
def main() -> None:
    """QuickAPI - Scaffold production-ready FastAPI projects in seconds."""
    pass


@main.command()
@click.argument("name")
@click.option("--description", "-d", default="A FastAPI application", help="Project description.")
@click.option("--database", "-db", type=click.Choice(["sqlite", "none"]), default="sqlite", help="Database backend.")
@click.option("--auth", is_flag=True, help="Include token-based authentication.")
@click.option("--no-docker", is_flag=True, help="Skip Docker files.")
@click.option("--no-tests", is_flag=True, help="Skip test files.")
@click.option("--no-cors", is_flag=True, help="Disable CORS middleware.")
@click.option("--port", "-p", default=8000, help="Default port number.")
@click.option("--python", "python_version", default="3.12", help="Python version for Dockerfile.")
@click.option("--output", "-o", default=".", type=click.Path(resolve_path=True), help="Output directory.")
def new(
    name: str,
    description: str,
    database: str,
    auth: bool,
    no_docker: bool,
    no_tests: bool,
    no_cors: bool,
    port: int,
    python_version: str,
    output: str,
) -> None:
    """Create a new FastAPI project.

    NAME is the project name (used as package name and directory).
    """
    config = ProjectConfig(
        name=name,
        description=description,
        database=database,
        include_docker=not no_docker,
        include_auth=auth,
        include_cors=not no_cors,
        include_tests=not no_tests,
        port=port,
        python_version=python_version,
    )

    header = Text()
    header.append("  QUICKAPI  ", style="bold white on bright_magenta")
    header.append(f"  Creating {name}", style="bold bright_white")
    console.print(Panel(header, border_style="bright_magenta", padding=(0, 1)))
    console.print()

    output_path = Path(output)
    project_path = output_path / name

    if project_path.exists():
        console.print(f"[red]Error:[/red] Directory '{name}' already exists.")
        raise SystemExit(1)

    created = scaffold_project(config, output_path)

    tree = Tree(f"[bold bright_magenta]{name}/[/bold bright_magenta]")
    rel_files = sorted(str(Path(f).relative_to(project_path)) for f in created)

    dirs_added: dict[str, Tree] = {}
    for rel in rel_files:
        parts = Path(rel).parts
        if len(parts) == 1:
            tree.add(f"[white]{parts[0]}[/white]")
        else:
            parent = parts[0]
            if parent not in dirs_added:
                dirs_added[parent] = tree.add(f"[bold cyan]{parent}/[/bold cyan]")
            dirs_added[parent].add(f"[white]{parts[1]}[/white]")

    console.print(tree)
    console.print()
    console.print(f"[bold green]Project created![/bold green] {len(created)} files generated.\n")
    console.print("[bold]Next steps:[/bold]")
    console.print(f"  cd {name}")
    console.print("  python -m venv .venv")
    console.print("  source .venv/bin/activate")
    console.print("  pip install -r requirements.txt")
    console.print(f"  uvicorn {name}.main:app --reload --port {port}")
    console.print(f"\n  API docs: [link]http://localhost:{port}/docs[/link]")


@main.command()
def templates() -> None:
    """List available project features."""
    console.print()
    console.print("[bold]Available features:[/bold]\n")

    features = [
        ("Database", "--database sqlite|none", "SQLite database with CRUD routes (default: sqlite)"),
        ("Authentication", "--auth", "Token-based auth with login endpoint"),
        ("Docker", "--no-docker to skip", "Dockerfile + docker-compose.yml (included by default)"),
        ("CORS", "--no-cors to skip", "Cross-origin middleware (included by default)"),
        ("Tests", "--no-tests to skip", "Pytest test suite (included by default)"),
    ]

    from rich.table import Table
    table = Table(border_style="bright_magenta", header_style="bold bright_white")
    table.add_column("Feature")
    table.add_column("Flag")
    table.add_column("Description")

    for name, flag, desc in features:
        table.add_row(f"[bold]{name}[/bold]", f"[cyan]{flag}[/cyan]", desc)

    console.print(table)
    console.print()
    console.print("[bold]Example:[/bold]")
    console.print("  quickapi new myapp --auth --database sqlite --port 3000\n")


@main.command()
@click.argument("description")
@click.option("--output", "-o", default=None, type=click.Path(resolve_path=True), help="Save generated files to this directory.")
def generate(description: str, output: str | None) -> None:
    """Generate FastAPI routes from a natural language description.

    Example: quickapi generate "a blog API with posts, comments, and user authentication"

    Requires one of: OPENAI_API_KEY, GEMINI_API_KEY, or NVIDIA_API_KEY.
    """
    from .ai_generate import ai_generate_api

    output_path = Path(output) if output else None
    ai_generate_api(description, output_dir=output_path)


@main.command()
@click.argument("description")
@click.option("--routes-file", "-r", default=None, type=click.Path(exists=True), help="Existing routes.py to extend.")
def add_endpoint(description: str, routes_file: str | None) -> None:
    """Generate a single endpoint from a description.

    Example: quickapi add-endpoint "search items by name with pagination"

    Requires one of: OPENAI_API_KEY, GEMINI_API_KEY, or NVIDIA_API_KEY.
    """
    from .ai_generate import ai_add_endpoint

    existing = ""
    if routes_file:
        existing = Path(routes_file).read_text()

    ai_add_endpoint(description, existing_routes=existing)


if __name__ == "__main__":
    main()
