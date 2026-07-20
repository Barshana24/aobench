"""aobench serve — launch the REST API or FastMCP server for engine access.

Thin CLI wrappers so the benchmarking engine is reachable over HTTP (REST) or as
MCP tools/resources without hand-writing a uvicorn script. The actual server
start is factored behind ``_serve_rest`` / ``_serve_mcp`` so the wiring is
testable without binding a socket.
"""

from __future__ import annotations

from typing import Any

import typer

from aobench.server.mcp import create_server
from aobench.server.rest.app import create_app

serve_app = typer.Typer(
    help="Run AOBench access servers (REST API / FastMCP).",
    no_args_is_help=True,
)


def _serve_rest(app: Any, host: str, port: int) -> None:  # pragma: no cover - blocks
    import uvicorn

    uvicorn.run(app, host=host, port=port)


def _serve_mcp(server: Any) -> None:  # pragma: no cover - blocks
    server.run()


@serve_app.command("rest")
def rest(
    host: str = typer.Option("127.0.0.1", help="Bind host."),
    port: int = typer.Option(8000, help="Bind port."),
) -> None:
    """Start the REST API (requires the `rest` extra: `uv sync --extra rest`)."""
    app = create_app()
    if app is None:
        typer.secho(
            "FastAPI is not installed. Install the REST extra: `uv sync --extra rest`.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    typer.secho(f"Serving AOBench REST API on http://{host}:{port}", fg=typer.colors.GREEN)
    _serve_rest(app, host, port)


@serve_app.command("mcp")
def mcp() -> None:
    """Start the FastMCP server over stdio (requires the `mcp` extra)."""
    try:
        server = create_server()
    except RuntimeError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(1) from exc
    typer.secho("Serving AOBench FastMCP server (stdio)…", fg=typer.colors.GREEN)
    _serve_mcp(server)
