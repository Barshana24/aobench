# AOBench

**Benchmark framework for evaluating AI agent systems in High-Performance Computing (HPC) environments.**

AOBench measures how well AI agents complete HPC operational tasks — job
scheduling, telemetry interpretation, energy reasoning, policy enforcement —
using the right tools, the right roles, and the right permissions. Instead of
running on live clusters, every task is evaluated against a deterministic
environment snapshot with mock HPC tools (SLURM, telemetry, RBAC, docs,
facility), so results are reproducible, portable, and safe to publish.

> **In one line:** AOBench is an AI agent benchmark for HPC — an HPC agent
> evaluation framework that is role-aware, permission-enforced, tool-using,
> trace-based, and reproducible.

**What / who / why (quotable summary):**

- AOBench (Agent Operations Benchmark) is an open-source Python benchmark framework for evaluating AI agents that operate High-Performance Computing (HPC) systems.
- AOBench helps researchers and engineers measure whether an AI agent completes HPC operational tasks — job scheduling, telemetry interpretation, energy reasoning, and policy enforcement — with the right tools, roles, and permissions.
- Use AOBench when you need reproducible, role-aware, permission-enforced evaluation of HPC agents against deterministic environment snapshots instead of live clusters.
- AOBench differs from general-purpose LLM-agent benchmarks because it is domain-specific to HPC operations, enforces role-based access control (RBAC), and scores the full execution trace rather than only the final answer.
- AOBench is not intended for measuring general-purpose reasoning, software-engineering, or web-browsing agents, and it does not execute against real production clusters.

## Requirements

- **Python** ≥ 3.10 (3.12 is used in the Docker image and CI, and is recommended).
- Optional: `openai`, `anthropic`, or `mcp` Python clients to drive the
  corresponding adapters.

See **[docs/getting-started/installation.md](docs/getting-started/installation.md)** for
the full installation guide — the Python package, the Docker CLI image, and the Docker
Compose service stack.

## Five benchmark principles

| Principle | Meaning |
|-----------|---------|
| **Role-aware** | The same question yields different answers and tool access depending on the requester role. |
| **Tool-using** | Agents are evaluated as systems that call HPC-native tools (SLURM, telemetry, docs, RBAC, facility). |
| **Permission-aware** | Success requires respecting RBAC and refusing out-of-scope requests. Permission violations hard-fail the task. |
| **Trace-based** | Evaluation considers the full execution trace — tool selection, arguments, sequence, and grounding — not just the final answer. |
| **Reproducible** | Runs target deterministic snapshot bundles, never live infrastructure. |

## Repository layout

```
AOBench/
├── src/aobench/           # Python package (installed by `pip install -e .`)
│   ├── cli/                # `aobench` typer app — 9 sub-commands
│   ├── schemas/            # Pydantic data models (task, trace, snapshot, …)
│   ├── loaders/, tasks/    # Task discovery, loading, dataset splits, RAG context
│   ├── environment/        # Snapshot validator, snapshot loader factory
│   ├── tools/              # Mock SLURM, telemetry, docs, RBAC, facility tools
│   ├── adapters/           # direct_qa, openai, anthropic, mcp
│   ├── runners/            # BenchmarkRunner, TraceWriter, ExecutionContext
│   ├── scorers/            # 12 scorers across 6 dimensions
│   ├── reports/            # JSON, HTML, slice, CLEAR scorecard reports
│   ├── exporters/          # Langfuse exporter (optional)
│   ├── leaderboard/        # FastAPI leaderboard service
│   ├── reproducibility/    # Artifact locking + paper-table targets
│   └── taxonomy/           # 24-leaf TRAIL-adapted HPC error taxonomy
│
├── benchmark/              # Static benchmark data (versioned in git)
│   ├── tasks/specs/        # 80 JSON task specs (all 10 QCATs × 5 roles)
│   ├── tasks/task_set_v1.json   # 36 HPC v1 tasks (Souza 2025 schema)
│   ├── tasks/task_set_v3.json   # v3 task index (80 tasks)
│   ├── tasks/dataset_splits.py  # 62 dev / 18 test split (~22% held-out)
│   ├── tasks/lite_manifest_v1.json  # AOBench-Lite curated subset
│   ├── environments/env_01–env_26/  # 26 deterministic snapshot bundles
│   ├── configs/            # scoring_profiles.yaml, hpc_tool_catalog.yaml,
│   │                       # error_taxonomy.yaml
│   └── qa/                 # AOBench-QA (~95 HPC operational queries)
│
├── data/                   # Generated artifacts
│   ├── runs/               # Per-run traces & results (gitignored)
│   ├── reports/            # Validity gate reports
│   ├── robustness/         # pass^k results
│   └── rubric_validation/  # Annotator profiles, response set, guides
│
├── prompts/judge/          # LLM-judge rubric + error taxonomy templates
├── docs/                   # Documentation (see Documentation section)
├── scripts/                # Bundle generation, validity gates, rubric tooling
└── tests/                  # 51 test files (unit + integration)
```

## Quick start

```bash
pip install -e ".[dev]"

# 1. Validate every task spec and environment bundle
aobench validate benchmark

# 2. Run one task end-to-end with the zero-tool baseline
aobench run task --task JOB_USR_001 --env env_01 --adapter direct_qa

# 3. Run a real adapter and emit a CLEAR scorecard
export OPENAI_API_KEY=sk-…
aobench run all --adapter openai:gpt-4o --split dev
aobench report json data/runs/<run_id>
aobench clear run data/runs/<run_id>
```

## Programmatic access & agent surfaces

Beyond the CLI, AOBench exposes the benchmark **engine** over four machine
surfaces so agents and pipelines can run and score tasks directly. Every surface
calls the same `BenchmarkService` façade — transports carry no scoring logic, so
CLEAR scores are identical across all of them.

| Surface | Start it with | What it exposes |
|---------|---------------|-----------------|
| **REST / FastAPI** | `aobench serve rest` (extra: `rest`) | `/v1/*` HTTP endpoints — run, score, report, trace, compare, robustness, datasets, async jobs, SSE progress |
| **MCP / FastMCP** | `aobench serve mcp` (extra: `mcp`) | MCP tools (`run_task`, `score_trace`, `validate_benchmark`, `robustness`) + `aobench://` resources |
| **A2A (Agent2Agent)** | evaluation scorers + adapter core | Agent-Card conformance, delegation / comms-cost / attribution / lifecycle / card-poisoning scorers |
| **CLI / terminal track** | evaluation scorers + adapter core | Mock Slurm shims, destructive-command guard, end-state verification |

```bash
uv sync --extra rest --extra mcp     # install both server extras (list together)
aobench serve rest --host 0.0.0.0 --port 8000
aobench serve mcp                     # stdio, for an MCP client to spawn
```

See the [programmatic-access guide](docs/guides/programmatic-access.md) and the
[serving tutorial](docs/tutorials/serving-the-benchmark.md) for end-to-end
walkthroughs, and [ROADMAP.md](ROADMAP.md) for surface status and what's next.

## Implemented scope (v0.3)

| Item | Count | Location |
|------|-------|----------|
| Tasks | 80 across 10 QCATs × 5 roles | `benchmark/tasks/specs/` |
| Environments | 26 deterministic snapshot bundles | `benchmark/environments/env_01`…`env_26` |
| Roles (scored) | 5 — `scientific_user`, `sysadmin`, `facility_admin`, `researcher`, `system_designer` | `src/aobench/schemas/task.py` |
| QCATs (scored) | 10 — `JOB`, `MON`, `ENERGY`, `PERF`, `DATA`, `SEC`, `FAC`, `ARCH`, `AIOPS`, `DOCS` | `benchmark/tasks/specs/` |
| Adapters | 4 — `direct_qa`, `openai`, `anthropic`, `mcp` | `src/aobench/adapters/` |
| Mock tool families | 5 — slurm, docs, rbac, telemetry, facility | `src/aobench/tools/` |
| Scorers | 12 across 6 dimensions | `src/aobench/scorers/` |
| Scoring profiles | `alpha0_minimal`, `alpha1_grounding`, `default_hpc_v01` | `benchmark/configs/scoring_profiles.yaml` |
| Tests | 1048 passing | `tests/` |

The 6 evaluation dimensions and their `default_hpc_v01` weights:

| Dimension | Weight | Scorer |
|-----------|--------|--------|
| Outcome correctness | 0.30 | `OutcomeScorer` (or `HybridScorer`) |
| Tool-use correctness | 0.20 | `ToolUseScorer` (BFCL-decomposed) |
| Governance / RBAC | 0.20 | `GovernanceScorer` |
| Grounding | 0.15 | `GroundingScorer` |
| Robustness (pass^k) | 0.10 | `RobustnessScorer` |
| Efficiency | 0.05 | `EfficiencyScorer` |

The CLEAR scorecard (`aobench clear run`) aggregates Efficacy, Assurance,
Reliability, Cost, and Latency into a single comparable score per model.

## Use cases

- **Compare models as HPC agents.** Run the same task suite across `openai`,
  `anthropic`, and `mcp` adapters and rank them with a single CLEAR scorecard.
- **Test tool-use and grounding.** Check whether an agent selects the right
  HPC-native tool (SLURM, telemetry, docs, RBAC, facility) with correct
  arguments and grounds its answer in the environment snapshot.
- **Verify permission safety.** Confirm an agent respects role-based access
  control and refuses out-of-scope requests — permission violations hard-fail
  the task.
- **Reproduce and publish results.** Evaluate against deterministic snapshot
  bundles so runs are portable and safe to publish without live-cluster access.
- **Author new tasks and environments.** Extend the 80-task / 26-environment
  corpus using the versioned JSON specs and snapshot format.

## Comparison and alternatives

AOBench is a **domain-specific** benchmark for HPC operations. It complements,
rather than replaces, general-purpose agent benchmarks:

| Benchmark | Primary domain | How AOBench differs |
|-----------|----------------|---------------------|
| General LLM-agent benchmarks (e.g. AgentBench, GAIA) | Broad assistant / reasoning tasks | AOBench targets HPC operational tasks with role-aware RBAC and deterministic HPC snapshots. |
| Tool-use / function-calling benchmarks (e.g. τ-bench, BFCL) | General tool and function calling | AOBench scores tool use *within HPC scenarios* (SLURM, telemetry, facility) and combines it with governance, grounding, robustness, and efficiency. AOBench's `ToolUseScorer` is BFCL-decomposed. |
| Software-engineering agent benchmarks (e.g. SWE-bench) | Code repair / repositories | AOBench evaluates HPC operations, not software patches. |

Choose AOBench when the question is specifically *"can this agent operate an HPC
system correctly, safely, and within its role?"* For general reasoning,
web-browsing, or code-repair agents, use the corresponding general-purpose
benchmark above.

## Limitations / when not to use

- **Not a live-cluster test.** AOBench runs against mock tools and deterministic
  snapshots by design; it does not execute against real production HPC
  infrastructure and does not measure real-world side effects.
- **HPC-scoped.** The corpus covers 5 roles, 10 QCATs, 80 tasks, and 26
  environments. It is not a general-purpose reasoning, web, or coding benchmark.
- **API keys required for hosted models.** The `openai` and `anthropic` adapters
  need the corresponding API keys and incur provider cost; the `direct_qa`
  baseline runs without tools for reference.
- **Early-stage (v0.x).** Scope, schemas, and scoring profiles are still
  evolving between minor versions.

## FAQ

**What is AOBench?**
AOBench (Agent Operations Benchmark) is an open-source Python framework for
evaluating AI agents that operate HPC systems. It scores agents on HPC
operational tasks against deterministic environment snapshots with mock HPC
tools.

**How does AOBench evaluate HPC agents?**
Each task runs an agent (via an adapter) against a deterministic snapshot with
mock SLURM, telemetry, docs, RBAC, and facility tools. AOBench records the full
execution trace and scores it across six dimensions — outcome correctness,
tool-use correctness, governance/RBAC, grounding, robustness (pass^k), and
efficiency — then aggregates results into a CLEAR scorecard (Efficacy,
Assurance, Reliability, Cost, Latency).

**How is AOBench different from general LLM-agent benchmarks?**
General benchmarks measure broad assistant, reasoning, tool-use, or
software-engineering ability. AOBench is domain-specific to HPC operations,
enforces role-based access control (permission violations hard-fail), and scores
the whole trace rather than only the final answer.

**Do I need a live HPC cluster to run AOBench?**
No. AOBench runs entirely against deterministic snapshot bundles and mock tools,
so it is portable and safe to publish.

**Which agents and models can I evaluate?**
Any model reachable through the `openai`, `anthropic`, or `mcp` adapters, plus a
tool-free `direct_qa` baseline for reference.

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/framework/index.md](docs/framework/index.md) | Documentation map |
| [docs/framework/system-architecture.md](docs/framework/system-architecture.md) | **Authoritative system architecture** — components, data flow, scoring pipeline, CLEAR scorecard |
| [docs/framework/overview.md](docs/framework/overview.md) | Principles and v0.1 scope |
| [docs/framework/background.md](docs/framework/background.md) | Motivation and related work |
| [docs/framework/architecture.md](docs/framework/architecture.md) | Benchmark design (layers, entities, workflow) |
| [docs/framework/implementation.md](docs/framework/implementation.md) | Developer guide to the codebase |
| [docs/framework/environments.md](docs/framework/environments.md) | Snapshot format |
| [docs/framework/evaluation.md](docs/framework/evaluation.md) | Evaluation protocol, trace and result schemas |
| [docs/framework/taxonomy.md](docs/framework/taxonomy.md) | Roles, QCATs, knowledge sources, RBAC |
| [docs/framework/scoring-dimensions.md](docs/framework/scoring-dimensions.md) | Per-scorer reference |
| [docs/COMMANDS.md](docs/reference/commands.md) | CLI command reference (incl. `aobench serve`) |
| [docs/guides/programmatic-access.md](docs/guides/programmatic-access.md) | REST + MCP programmatic access guide |
| [docs/tutorials/serving-the-benchmark.md](docs/tutorials/serving-the-benchmark.md) | Tutorial — serve the engine and drive it over REST/MCP |
| [ROADMAP.md](ROADMAP.md) | Surface status and planned work |
| [docs/environments-overview.md](docs/reference/environments-overview.md) | Inventory of all 20 environment bundles |
| [docs/adapters-and-tools.md](docs/guides/adapters-and-tools.md) | Plain-English adapter and tool guide |
| [docs/architecture-flowchart.md](docs/reference/architecture-flowchart.md) | System diagrams |
| [docs/langfuse-integration.md](docs/guides/langfuse-integration.md) | Observability backend |
| [docs/paper_reproduction_guide.md](docs/guides/paper-reproduction.md) | Reproducing v0.1 paper tables |
| [CHANGELOG.md](CHANGELOG.md) | Release notes |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guide |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting and threat model |

Full documentation site: <https://mskazemi.com/aobench/>

Source: [github.com/MSKazemi/aobench](https://github.com/MSKazemi/aobench) ·
Mirror: [gitlab.com/mskazemi/aobench](https://gitlab.com/mskazemi/aobench)

## AOBench-QA

The `benchmark/qa/` directory embeds the AOBench-QA dataset — ~95 HPC
operational queries with role-specific variants and structured taxonomies. It
is consumed by the `direct_qa` baseline and seeds task design for the v1 HPC
task set.

## Citation

If you use AOBench in your research, please cite it. Citation metadata is
provided in [CITATION.cff](CITATION.cff); GitHub renders a "Cite this
repository" button from that file.

```
Seyedkazemi Ardebili, Mohsen. AOBench: A Trace-Driven, Role-Aware Benchmark for
Agent Operations in Realistic Environments. https://github.com/MSKazemi/aobench
```

The source is mirrored at <https://gitlab.com/mskazemi/aobench>.

## License

Apache 2.0 — see [LICENSE](LICENSE).
