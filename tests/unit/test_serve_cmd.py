"""Tests for the `aobench serve` CLI (REST / MCP launch wiring)."""

from __future__ import annotations

from typer.testing import CliRunner

from aobench.cli import serve_cmd

runner = CliRunner()


def test_serve_rest_wires_host_port(monkeypatch):
    calls = {}
    monkeypatch.setattr(serve_cmd, "create_app", lambda: object())
    monkeypatch.setattr(serve_cmd, "_serve_rest",
                        lambda app, host, port: calls.update(host=host, port=port))
    result = runner.invoke(serve_cmd.serve_app, ["rest", "--host", "0.0.0.0", "--port", "9100"])
    assert result.exit_code == 0
    assert calls == {"host": "0.0.0.0", "port": 9100}


def test_serve_rest_missing_fastapi_errors(monkeypatch):
    monkeypatch.setattr(serve_cmd, "create_app", lambda: None)   # FastAPI absent
    result = runner.invoke(serve_cmd.serve_app, ["rest"])
    assert result.exit_code == 1
    assert "FastAPI is not installed" in result.output


def test_serve_mcp_wires_server(monkeypatch):
    started = {}
    monkeypatch.setattr(serve_cmd, "create_server", lambda: "SERVER")
    monkeypatch.setattr(serve_cmd, "_serve_mcp", lambda server: started.update(s=server))
    result = runner.invoke(serve_cmd.serve_app, ["mcp"])
    assert result.exit_code == 0
    assert started == {"s": "SERVER"}


def test_serve_mcp_missing_fastmcp_errors(monkeypatch):
    def _raise() -> object:
        raise RuntimeError("fastmcp is not installed. Install the MCP extra")

    monkeypatch.setattr(serve_cmd, "create_server", _raise)
    result = runner.invoke(serve_cmd.serve_app, ["mcp"])
    assert result.exit_code == 1
    assert "fastmcp is not installed" in result.output


def test_serve_no_args_shows_help():
    result = runner.invoke(serve_cmd.serve_app, [])
    assert result.exit_code != 0 or "rest" in result.output
