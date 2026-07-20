"""FastMCP server binding for AOBench (spec-0004).

Registers the pure handlers from ``handlers.py`` as FastMCP tools + resources.
Targets MCP spec 2025-11-25 and FastMCP v2 (bare ``@mcp.tool`` decorators).
"""

from __future__ import annotations

import os
from typing import Any, Optional

from aobench.server.mcp import handlers
from aobench.service import BenchmarkService

try:
    from fastmcp import FastMCP

    FASTMCP_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only when extra absent
    FASTMCP_AVAILABLE = False


def _build_auth() -> Any:
    """Build a JWTVerifier from env when configured, else None (stdio/local = open).

    Set AOBENCH_MCP_JWKS_URI / AOBENCH_MCP_ISSUER / AOBENCH_MCP_AUDIENCE to enable
    OAuth 2.1 resource-server auth on the HTTP transport (spec-0004 R5).
    """
    jwks = os.environ.get("AOBENCH_MCP_JWKS_URI")
    if not jwks:
        return None
    from fastmcp.server.auth.providers.jwt import JWTVerifier

    return JWTVerifier(
        jwks_uri=jwks,
        issuer=os.environ.get("AOBENCH_MCP_ISSUER"),
        audience=os.environ.get("AOBENCH_MCP_AUDIENCE", "aobench-mcp"),
    )


def create_server(service: Optional[BenchmarkService] = None) -> Any:
    """Build and return a FastMCP server exposing the AOBench engine.

    Raises RuntimeError with an actionable message when ``fastmcp`` is absent
    (install ``aobench[mcp]``).
    """
    if not FASTMCP_AVAILABLE:
        raise RuntimeError(
            "fastmcp is not installed. Install the MCP extra: `uv sync --extra mcp` "
            "(or `pip install 'aobench[mcp]'`)."
        )

    svc = service or BenchmarkService(
        benchmark_root=os.environ.get("AOBENCH_BENCHMARK_ROOT", "benchmark"),
        output_root=os.environ.get("AOBENCH_OUTPUT_ROOT", "data/runs"),
    )

    mcp = FastMCP(name="AOBench Benchmark Server", auth=_build_auth())

    # ---------------- tools (side effects) ---------------- #
    @mcp.tool
    def run_task(task_id: str, env_id: str, adapter: str = "direct_qa",
                 role: str | None = None, seed: int | None = None) -> dict[str, Any]:
        """Run one AOBench task against an environment snapshot; returns run_id + score."""
        return handlers.run_task(svc, task_id, env_id, adapter, role, seed)

    @mcp.tool
    def score_trace(task_id: str, trace: dict[str, Any]) -> dict[str, Any]:
        """Score a captured trace against a task without re-running the agent."""
        return handlers.score_trace(svc, task_id, trace)

    @mcp.tool
    def validate_benchmark() -> dict[str, Any]:
        """Return loadable task/env counts (lightweight benchmark health check)."""
        return handlers.validate_benchmark(svc)

    @mcp.tool
    def robustness(task_id: str, env_id: str, adapter: str = "direct_qa",
                   n: int = 5) -> dict[str, Any]:
        """Run a task n times; returns score mean/stdev (consistency check)."""
        return handlers.robustness(svc, task_id, env_id, adapter, n)

    # ---------------- resources (read-only) ---------------- #
    @mcp.resource("aobench://catalog/tasks")
    def catalog_tasks() -> str:
        """All benchmark task specs with QCAT/role/split metadata."""
        return handlers.catalog_tasks(svc)

    @mcp.resource("aobench://catalog/tasks/{task_id}")
    def catalog_task(task_id: str) -> str:
        """Metadata for one task."""
        return handlers.catalog_task(svc, task_id)

    @mcp.resource("aobench://catalog/envs")
    def catalog_envs() -> str:
        """All environment bundles with manifest fingerprints."""
        return handlers.catalog_envs(svc)

    @mcp.resource("aobench://runs/{run_id}/report")
    def run_report(run_id: str) -> str:
        """Scorecard summary for a completed run."""
        return handlers.run_report(svc, run_id)

    @mcp.resource("aobench://runs/{run_id}/trace")
    def run_trace(run_id: str) -> str:
        """Full execution trace for a completed run."""
        return handlers.run_trace(svc, run_id)

    return mcp
