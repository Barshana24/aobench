"""AOBench benchmark-engine REST API (spec-0003, Feature 1).

Distinct from ``aobench.leaderboard.api`` (submission-only). Exposes the engine
(run/score/report/trace/compare) over HTTP via the shared service façade.
Ships behind ``aobench[rest]``; ``create_app()`` returns ``None`` when FastAPI
is not installed.
"""

from __future__ import annotations

from aobench.server.rest.app import create_app

__all__ = ["create_app"]
