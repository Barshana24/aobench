# AOBench Roadmap

Status of the multi-surface benchmark platform. The authoritative feature→module→test
matrix lives in [`design/vision/implementation-status.md`](design/vision/implementation-status.md);
this file is the high-level view.

Legend: ✅ shipped · 🟡 partial (usable core shipped, sub-feature deferred) · ⛔ deferred (external dependency).

## Shipped

### Core benchmark (v0.3)
- 80 tasks × 26 environment bundles, 5 roles, 10 QCATs, 12 scorers / 6 dimensions.
- CLEAR scorecard (Cost / Latency / Efficacy / Assurance / Reliability).
- M100 ExaData-grounded environments and tasks.

### Multi-surface engine access (v0.4, in progress on `feat/aobench-futures-30-features`)
Every surface calls the shared `BenchmarkService` façade — identical scores across transports.

| Surface | Status | Notes |
|---------|--------|-------|
| REST API (FastAPI) — `aobench serve rest` | ✅ | run/score/report/trace/compare/robustness/datasets + async jobs + SSE; API-key→role auth + rate limiting |
| FastMCP server — `aobench serve mcp` | ✅ | tools (`run_task`/`score_trace`/`validate_benchmark`/`robustness`) + `aobench://` resources; JWT auth hook |
| A2A evaluation | ✅ | Agent-Card conformance + delegation / comms-cost / attribution / lifecycle / card-poisoning scorers |
| CLI / terminal evaluation | ✅ | mock Slurm shims, destructive-command guard, end-state verifier |

### Cross-cutting (v0.4)
- OTel-GenAI trace exporter · deterministic replay cassettes · in-toto attestation.
- Carbon/cost/CO₂e accounting + contamination guard · pass^k + bootstrap CIs (measurement rigor).
- Futuristic HPC scorers: incident RCA (+ log evidence), escalation/abstention, carbon-aware
  scheduling, predictive maintenance.
- MCP-usage scorers: tool-selection, injection-resistance, elicitation.

## In progress / partial (🟡)

| Item | Shipped | Deferred half |
|------|---------|---------------|
| Async run queue (F2) | job registry + async submission (single process) | durable arq/Redis worker |
| Event delivery (F3) | SSE + polling | outbound webhooks |
| Typed SDK (F4) | REST auth + OpenAPI | generated client SDK |
| Datasets/Experiments API (F5) | datasets read side | experiment-result persistence DB |
| MCP auth (F7) | JWT scaffold | full OIDC → RBAC mapping |
| A2A access (F12) | adapter core (injected transport) | live A2A HTTP transport |
| CLI access (F19) | adapter core (injected executor) | Docker/gVisor executor |
| Futuristic HPC (F30) | carbon-aware + predictive-maintenance scorers | thermal digital-twin surrogate |

## Deferred — external dependency (⛔)

- **F8** — async MCP Tasks primitive (experimental in MCP 2025-11-25).
- **F18** — containerized HPC terminal runner + tiered sandbox (needs Docker/gVisor, ADR 0006).

## Next milestones

1. **Land `feat/aobench-futures-30-features`** into the mainline and cut v0.4.
2. **Infra features** as dependencies come online: Redis worker (F2), Docker sandbox (F18/F19),
   live A2A transport (F12), experiment DB (F5), OIDC (F7), SDK codegen (F4), thermal twin (F30).
3. **Reporting suite** (spec-0002) — 14 report renderers on the data→stats→model→render pipeline.
4. Clean up 8 pre-existing test failures in `governance_report` / `run_cmd` / ablation scripts.
