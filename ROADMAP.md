# AOBench Roadmap

Status of the multi-surface benchmark platform.

**Want to help?** Every item below that isn't shipped has a tracking issue.
Browse them by effort — [`effort: small`](https://github.com/MSKazemi/aobench/labels/effort%3A%20small)
is the best place to start — or by area, or pick from
[**good first issues**](https://github.com/MSKazemi/aobench/labels/good%20first%20issue).
Work is grouped into [milestones](https://github.com/MSKazemi/aobench/milestones).

Legend: ✅ shipped · 🟡 partial (usable core shipped, sub-feature deferred) · ⛔ deferred (external dependency).

## Shipped

### Core benchmark (v0.3)
- 88 tasks × 29 environment bundles, 5 roles, 10 QCATs, 12 scorers / 6 dimensions.
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
| Async run queue (F2) | job registry + async submission (single process) | durable arq/Redis worker — [#10](https://github.com/MSKazemi/aobench/issues/10) |
| Event delivery (F3) | SSE + polling | outbound webhooks — [#11](https://github.com/MSKazemi/aobench/issues/11) |
| Typed SDK (F4) | REST auth + OpenAPI | generated client SDK — [#12](https://github.com/MSKazemi/aobench/issues/12) |
| Datasets/Experiments API (F5) | datasets read side | experiment-result persistence DB — [#13](https://github.com/MSKazemi/aobench/issues/13) |
| MCP auth (F7) | JWT scaffold | full OIDC → RBAC mapping — [#14](https://github.com/MSKazemi/aobench/issues/14) |
| A2A access (F12) | adapter core (injected transport) | live A2A HTTP transport — [#15](https://github.com/MSKazemi/aobench/issues/15) |
| CLI access (F19) | adapter core (injected executor) | Docker/gVisor executor — [#19](https://github.com/MSKazemi/aobench/issues/19) |
| Futuristic HPC (F30) | carbon-aware + predictive-maintenance scorers | thermal digital-twin surrogate — [#17](https://github.com/MSKazemi/aobench/issues/17) |

## Deferred — external dependency (⛔)

- **F8** — async MCP Tasks primitive (experimental in MCP 2025-11-25) — [#18](https://github.com/MSKazemi/aobench/issues/18).
- **F18** — containerized HPC terminal runner + tiered sandbox (needs a sandboxing dependency) — [#19](https://github.com/MSKazemi/aobench/issues/19).

## Next milestones

1. **Land `feat/aobench-futures-30-features`** into the mainline and cut v0.4.
2. **Infra features** as dependencies come online: Redis worker (F2), Docker sandbox (F18/F19),
   live A2A transport (F12), experiment DB (F5), OIDC (F7), SDK codegen (F4), thermal twin (F30).
3. **Reporting suite** — report renderers on the data→stats→model→render pipeline — [#16](https://github.com/MSKazemi/aobench/issues/16).
4. Clean up the pre-existing test failures in `governance_report` / `run_cmd` / ablation scripts — [#8](https://github.com/MSKazemi/aobench/issues/8).
5. Quality debt: lint `scripts/` — [#6](https://github.com/MSKazemi/aobench/issues/6) · strict typing — [#7](https://github.com/MSKazemi/aobench/issues/7).
