"""AI-powered API generation from natural language descriptions."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax

from .ai_client import query_ai, get_provider_name

console = Console()

SYSTEM_PROMPT = """\
You are QuickAPI AI, an expert FastAPI developer. Given a natural language description of an API,
generate production-ready FastAPI code. Include:
- Pydantic models for request/response
- FastAPI route handlers with proper HTTP methods
- Type hints and docstrings
- Error handling with HTTPException
- SQLite database operations where needed

Return ONLY a JSON object with these keys:
- "routes_code": string containing the complete routes.py code
- "models_code": string containing the complete models.py code
- "description": brief description of what was generated

Do NOT include markdown formatting. Return raw JSON only."""


def ai_generate_api(description: str, output_dir: Path | None = None) -> dict[str, str] | None:
    """Generate FastAPI routes from a natural language description."""
    provider = get_provider_name()
    if provider == "none":
        console.print("[red]No AI API key found.[/red]")
        console.print("Set one of: [bold]OPENAI_API_KEY[/bold], [bold]GEMINI_API_KEY[/bold], or [bold]NVIDIA_API_KEY[/bold]")
        return None

    header = Text()
    header.append("  AI GENERATE  ", style="bold white on bright_magenta")
    header.append(f"  powered by {provider}", style="bold bright_white")
    console.print(Panel(header, border_style="bright_magenta", padding=(0, 1)))
    console.print()

    prompt = f"""Generate a FastAPI API based on this description:

"{description}"

Requirements:
- Use FastAPI with proper type hints
- Include Pydantic models for all request/response schemas
- Use SQLite for persistence (via sqlite3 module)
- Include proper error handling (404, 400, etc.)
- Add docstrings to all endpoints
- Use async route handlers
- Follow REST conventions (GET for list/detail, POST for create, PUT for update, DELETE for delete)

Return a JSON object with "routes_code", "models_code", and "description" keys.
Return ONLY valid JSON, no markdown."""

    with console.status(f"[bold magenta]Generating API with {provider}...", spinner="dots"):
        response = query_ai(prompt, system_prompt=SYSTEM_PROMPT)

    try:
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[1].rsplit("```", 1)[0]
        result = json.loads(response)
    except (json.JSONDecodeError, IndexError):
        console.print("[red]Error parsing AI response. Showing raw output:[/red]\n")
        console.print(response)
        return None

    console.print(f"[bold green]Generated:[/bold green] {result.get('description', 'API code')}\n")

    routes_code = result.get("routes_code", "")
    models_code = result.get("models_code", "")

    if routes_code:
        console.print(Panel("[bold]routes.py[/bold]", border_style="cyan"))
        console.print(Syntax(routes_code, "python", theme="monokai", line_numbers=True))
        console.print()

    if models_code:
        console.print(Panel("[bold]models.py[/bold]", border_style="cyan"))
        console.print(Syntax(models_code, "python", theme="monokai", line_numbers=True))
        console.print()

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        if routes_code:
            (output_dir / "routes.py").write_text(routes_code)
        if models_code:
            (output_dir / "models.py").write_text(models_code)
        console.print(f"[bold green]Files saved to:[/bold green] {output_dir}")

    return result


def ai_add_endpoint(description: str, existing_routes: str = "") -> str | None:
    """Generate a single endpoint to add to existing routes."""
    provider = get_provider_name()
    if provider == "none":
        console.print("[red]No AI API key found.[/red]")
        return None

    prompt = f"""Add a new endpoint to this existing FastAPI router based on the description.

Description: "{description}"

{"Existing routes.py:" + chr(10) + existing_routes if existing_routes else "No existing routes."}

Return ONLY the Python code for the new endpoint function(s) and any new Pydantic models needed.
Include necessary imports at the top. Do NOT include markdown formatting."""

    system = "You are a FastAPI expert. Generate clean, production-ready endpoint code. Return only Python code, no markdown."

    with console.status(f"[bold magenta]Generating endpoint with {provider}...", spinner="dots"):
        response = query_ai(prompt, system_prompt=system)

    response = response.strip()
    if response.startswith("```"):
        response = response.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    console.print(Panel("[bold]Generated Endpoint[/bold]", border_style="cyan"))
    console.print(Syntax(response, "python", theme="monokai", line_numbers=True))
    console.print()

    return response
