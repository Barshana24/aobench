# Changelog

## Unreleased

### Added — Installation & running guide (docs)

- New canonical **[Installation & Running](docs/getting-started/installation.md)** page
  consolidating all three ways to install and run AOBench: the Python package (uv/pip with
  the optional-extras matrix), the Docker CLI image (`docker build` / `make repro-docker`),
  and the Docker Compose service stack (`make stack-up` → Langfuse + leaderboard). Wired into
  the MkDocs nav under a new **Getting Started** section.

### Fixed — Documentation accuracy

- Corrected the advertised Python floor to **≥ 3.10** (matching `requires-python`) in the docs
  landing page badge and `README.md`; noted 3.12 is used in Docker/CI.
- Replaced the misleading `pip install "aobench[openai]"` PyPI-style command on the docs home
  with the real from-source install (AOBench is not yet published to PyPI).
- Repaired two broken cross-links in the serving tutorial (`ROADMAP.md` → GitHub blob,
  an internal design note → the in-docs system-architecture page); `mkdocs build
  --strict` now passes clean.

### Changed — Repo consolidation (2026-07-16)

- Consolidated the working tree; internal dataset-tooling path references were updated
  accordingly. No change to the published package, the benchmark corpus, or any API.

### Added — Multi-surface engine access (AOBench Futures, P0)

- **Service façade** (`aobench.service.BenchmarkService`): one transport-agnostic API
  (`submit_run`/`get_run`/`get_trace`/`get_report`/`score_trace`/`list_tasks`/`list_envs`/
  `compare`/`robustness`) wrapping the existing `BenchmarkRunner`, with a typed error
  hierarchy and an ADR-0005 reproducibility fingerprint. All new surfaces call it, so CLEAR
  scores never diverge across surfaces.
- **Benchmark-engine REST API** (`aobench.server.rest`, extra `aobench[rest]`): FastAPI app
  exposing `/v1/runs`, `.../trace`, `.../report`, `.../events` (SSE live trace), `/v1/score`,
  `/v1/compare`, `/v1/robustness`, `/v1/tasks`, `/v1/envs`, `/v1/datasets`; API-key→role auth,
  rate limiting, OpenAPI 3.1. Distinct from the submission-only leaderboard API.
- **FastMCP server** (`aobench.server.mcp`, extra `aobench[mcp]`): exposes the engine as MCP
  tools (`run_task`, `score_trace`, `validate_benchmark`, `robustness`) and resources
  (`aobench://catalog/tasks|envs`, `aobench://runs/{id}/report|trace`); JWT-auth hook for the
  HTTP transport. (AOBench-as-MCP-server, distinct from the existing MCP-client adapter.)
- **OTel-GenAI trace exporter** (`aobench.exporters.otel`, extra `aobench[otel]`): emits runs
  as OpenTelemetry GenAI spans (`gen_ai.*`) with an `aobench.*` extension namespace over OTLP
  (Langfuse-native); pure `Trace → spans` converter, content-capture gated, no-op when absent.
- **MCP elicitation-handling scorer + tool-scaling axis** (`aobench.scorers.mcp_scorers`,
  Feature 11): `score_elicitation_handling` scores whether an agent supplies a valid missing
  HPC parameter (partition/account/walltime) when the server elicits it, vs hallucinating a
  value or (correctly) abstaining on a truly unknowable one; `tool_scaling_retention` measures
  accuracy retention as decoy tools scale from a handful to dozens.
- **Futuristic HPC scorers** (`aobench.scorers.hpc_scorers`, Features 28 & 30): an incident
  root-cause-analysis scorer (`score_rca`) that credits correct root-cause-entity localization
  and mitigation, with mitigation credit gated on entity correctness (CFS); and a carbon-aware
  scheduling scorer (`score_carbon_aware_schedule`) that rewards shifting deferrable jobs to
  low-carbon-intensity windows within deadlines, normalized against the carbon-optimal schedule;
  and a predictive-maintenance scorer (`score_predictive_maintenance`) scoring failure
  predictions by lead-time-weighted precision/recall (earlier actionable warnings score higher);
  plus a log-analysis evidence sub-scorer (`score_log_evidence`, set-F1 over the log lines an
  agent cites as RCA evidence vs gold) with a `find_evidence_lines` regex helper.
- **Escalation + abstention scorer** (`aobench.scorers.escalation_scorer`, Feature 29): rewards
  correct human-escalation of irreversible/high-risk actions and abstention when a tool is
  missing or an action is RBAC-blocked; penalizes under-escalation (unilateral action) and
  over-escalation beyond a reviewer budget; a unilateral *critical* action is a hard-fail.
- **End-state verification scorer** (`aobench.cli_track.end_state`, Feature 21): Harbor-style
  grading that judges the final environment state (dot-path assertions over the post-run
  `slurm_state.json`, with critical assertions as hard-fails and optional weighting) rather than
  the agent's transcript — outcome-based scoring that resists reward-hacking.
- **CLI/shell agent adapter — pure core** (`aobench.cli_track.cli_adapter`, Feature 19):
  `build_cli_trace` translates a recorded shell command/output stream into the universal
  `Trace` (each command a `shell` tool-call step; a destructive command flags `hard_fail` via
  the Feature 22 guard), and `CLIAdapter(BaseAdapter)` runs it with an injected command source.
  The container executor (Feature 18, Docker/gVisor) plugs in as that source; the trace-building
  core is Docker-free and reuses the scorer layer unchanged.
- **CLI/terminal track** (`aobench.cli_track`, Features 20 & 22): a destructive-command
  guardrail scorer (`score_command_stream`) that flags catastrophic ops (recursive root delete,
  fork bomb, marking a node down, cancelling other users' jobs) as hard-fails and risky ops
  (rm -rf, sudo, piping remote scripts to a shell) as penalties; plus a mock Slurm CLI
  interpreter (`run_slurm_command`: squeue/scontrol/sacct/sbatch) over the shared JSON state so
  real terminal commands and the mock SlurmTool return the same ground truth.
- **A2A multi-agent evaluation** (`aobench.a2a`, Features 13–17): A2A schema (Agent Card,
  skills, delegation records, multi-agent trace, task-state enum); an Agent Card conformance
  harness (`check_agent_card`); and scorers for delegation quality, inter-agent communication
  cost, failure attribution (who-and-when), task-lifecycle protocol conformance
  (`score_task_lifecycle`, deterministic), and Agent-Card-poisoning robustness
  (`score_card_poisoning_resistance` — flags unsigned/over-scoped/non-conformant cards and
  hard-fails on delegation to a rogue worker or an RBAC breach) over a recorded
  orchestrator+worker run.
- **`aobench serve` CLI**: `aobench serve rest [--host --port]` and `aobench serve mcp` launch the
  REST API and FastMCP server directly from the CLI (with a graceful "install the extra" message
  when the optional dependency is absent), so the engine is reachable over HTTP or MCP without
  writing a uvicorn script.
- **Datasets read API** (`aobench.service`, Feature 5): `list_datasets` reports the versioned
  task corpus (`SPLIT_FROZEN_CORPUS_VERSION`) and real per-split task counts (all/dev/test/lite)
  from the frozen split definitions, replacing the `/v1/datasets` stub with a `DatasetInfo` model.
- **Async job submission** (`aobench.service.jobs`, Feature 2): `InMemoryJobRegistry` + `run_job`
  lifecycle core (thread-safe, submit-ordered; drives queued→running→completed|failed around a
  callable, capturing errors as job state rather than raising, and skipping cancelled jobs),
  wired into the façade (`enqueue_run`/`get_job`/`list_jobs`) and the REST API
  (`POST /v1/runs?wait=false` + `GET /v1/jobs[/{id}]`). Async submission works single-process
  today; a durable arq/Redis worker is a drop-in backend upgrade for crash-survivable sweeps.
- **A2A orchestrator adapter — pure core** (`aobench.a2a.adapter`, Feature 12): `build_multi_agent_trace`
  translates a recorded orchestrator→worker delegation-event stream into a `MultiAgentTrace`
  (first-seen worker order, `run_failed` inferred from failure states/culprit flags), and
  `A2AOrchestratorAdapter` runs it with an injected delegation source. The live A2A HTTP
  transport plugs in as that source; the trace-building core is network-free and feeds the
  A2A scorers (F14–F17) directly.
- **Run accounting + contamination guard** (`aobench.analysis`, Feature 26): `account_run`
  (exact token cost + estimated energy/CO2e feeding CLEAR Cost) and `check_contamination`
  (cross-session output-diversity memorization probe + canary-leak detection for public-exposure
  training-set contamination).
- **Result attestation** (`aobench.reproducibility.attestation`, Feature 25): builds an
  in-toto (ITE-6) statement binding a run's result + trace + environment fingerprint and
  produces a detached HMAC-SHA256 signature (offline; Sigstore keyless signing optional) for
  tamper-evident leaderboard submissions.
- **Deterministic replay engine** (`aobench.reproducibility.replay`, Feature 24): cassette
  record/replay keyed by `(task, env, seed, model, prompt)` with `live`/`replay`/`auto` modes —
  bit-reproducible, zero-API-cost re-runs for CI and offline regrading.
- **MCP-usage scorers** (`aobench.scorers.mcp_scorers`, Features 9 & 10): `MCPToolSelectionScorer`
  (tool-selection F1 + argument-schema validity + call-order/dependency compliance against the
  gold trajectory) and `MCPInjectionResistanceScorer` (detects adversarial content in tool
  outputs and scores whether the agent resisted vs. was manipulated into a forbidden action/leak).
- **Measurement rigor** (`aobench.analysis.rigor`, Feature 27): `pass^k` reliability (unbiased
  combinatorial estimator), seeded percentile bootstrap confidence intervals, and a
  `summarize_scores` helper. Surfaced through `robustness` on the façade, REST `/v1/robustness`,
  and the MCP `robustness` tool (pass@1, pass^k, and a 95% CI over repeated runs).

### Documentation

- `docs/guides/programmatic-access.md`: user guide for the new REST API and FastMCP server —
  installing the `rest`/`mcp` extras, starting each server, authentication (API-key→role for
  REST, OAuth 2.1/JWKS for MCP), endpoint/tool/resource reference tables, and worked
  curl + FastMCP-client examples. Added to the Guides nav.
- `docs/tutorials/serving-the-benchmark.md`: new hands-on tutorial — install extras, start the
  REST/MCP servers, run+score a task synchronously and asynchronously (jobs + SSE), and verify
  surfaces agree with the CLI. Added a Tutorials nav section.
- `docs/reference/commands.md`: documented the `aobench serve rest|mcp` command (options,
  `/v1/*` endpoint table, MCP tools/resources, examples) plus Quick-Reference rows.
- `README.md`: new "Programmatic access & agent surfaces" section (REST/MCP/A2A/CLI table +
  `aobench serve` quick start) and doc links.
- `ROADMAP.md`: new roadmap — surface status (shipped/partial/deferred) and next milestones.
- `docs/reference/environments-overview.md`: add the six M100 ExaData-grounded bundles
  (`env_m100_01`–`env_m100_06`) to the overview index, with scenario, scored roles, and rebuild
  instructions.

### Fixed

- Completed the ExaBench→AOBench gym-module rename (`gym/exabench_env.py` →
  `gym/aobench_env.py`); the stale filename left `aobench.gym.__init__` importing a
  non-existent module, which broke collection of the **entire** test suite.
- `cli/validate_cmd.py`: the oracle-check path referenced an unimported `pathlib`
  (`NameError`); now uses the already-imported `Path`.
- `adapters/base.py` and `adapters/direct_qa_adapter.py`: the `run()` `ExecutionContext`
  annotation referenced an undefined name; added a `TYPE_CHECKING` import.
- `test_governance_report.py`: assertions executed outside the `TemporaryDirectory` context,
  so the generated report was deleted before the existence check (test always failed).
- Test suite restored to green (1451 passing) after multi-surface-development churn; also
  fixed stale `rbac`/`multi-model` test expectations.
- `cli/rescore_cmd.py`: `aobench rescore` was a pass-through no-op — it copied the pre-existing
  scores out of each trace instead of scoring. It now genuinely replays every stored trace
  through the full `AggregateScorer` and writes fresh `BenchmarkResult` files. The invocation is
  flattened from `aobench rescore rescore <dir>` to `aobench rescore <dir>`, with a new
  `--benchmark-root` option. Added `scripts/rescore_governance.py` for a governance-only re-score
  with an old-vs-new mean + Wilson-CI comparison against the locked paper numbers.
- `tests/scripts/test_ablation_scripts.py`: fixtures still wrote the pre-refactor
  `<model>/results.jsonl` layout after the scripts moved to per-file `run_*/results/*.json`
  discovery, so all five affected cases read empty input. Fixtures now emit the current per-file
  layout (matching `TraceWriter`) and the malformed-input case tests a bad result *file*, not a
  JSONL line.

### Changed — Tooling / quality gates

- Added `types-PyYAML` and `pandas-stubs` dev dependencies and a scoped
  `[[tool.mypy.overrides]] ignore_missing_imports` for optional deps (jinja2/anthropic/langfuse).
- Typed bare `dict`/`list` generics, removed unused `# type: ignore` comments and dead code,
  and fixed ambiguous variable names — reducing strict-mypy errors from 201 to 86 (in progress)
  and restoring a clean `ruff` pass.

## v0.3.0 — 2026-06-19 — M100 ExaData grounding

### Scored real-baseline variant + governance calibration (Phase 3, 2026-06-18)

- **Real-baseline mode is now a *scored* variant.** All 8 `M100_*` task gold answers were
  rewritten to qualitative, mode-invariant form — asserting node identity, named-constant
  threshold crossings (84°C throttle, 1300W alert, 28/32°C), peer relationships and the
  recommended action, rather than sampled absolutes. The `OutcomeScorer` `semantic_match` path
  blends 60% fuzzy text + 40% numeric and credits reproducing each gold number within ±5%, so
  sampled magnitudes de-synced against real per-node traces; the retained numbers (job/node ids,
  hardware/policy constants, exit codes) hold in **both** distribution-sampled and real-baseline
  mode. Verified on `n1` against the real dataset (`--real-baselines --relative-anomalies`).
- **Governance calibration.** Added `hard_fail_conditions` to the 3 `scientific_user` tasks
  (`access_other_user_job`, `disclose_system_topology`, …), matching the existing corpus
  convention (admin tasks intentionally left empty). Governance now discriminates: GPT-4o tripped
  these on two user tasks (governance 0.0), while the do-nothing baseline is discounted by the
  engagement-aware CLEAR Assurance metric. No change to the global `GovernanceScorer` — the locked
  paper governance numbers are unaffected.
- **Gold-consistency guard.** `scripts/build_m100_bundles.py` now verifies (at the end of `main()`,
  raising on failure) that each env's generated telemetry satisfies the qualitative facts its gold
  answer relies on — in both modes — so a build that silently de-syncs from the scored gold is
  caught. New `tests/unit/test_m100_gold_consistency.py`.

### CLEAR scorecard — engagement-aware Assurance + full-panel Cost (2026-06-18)

- **Assurance (A)** recomputed as engagement-aware graded governance (mean `GovernanceScorer`
  score over runs that engaged a tool) instead of the binary RBAC-compliance rate; the legacy
  binary rate is retained as `governance_v01` for appendix reproducibility, and `EngagementRate`
  is derived from the same `tool_use` signal.
- `AIOPS_USR_001` excluded from primary scoring (known spec defect; dev split 59 → 58 scored
  tasks), kept in sync across `compute_stats.py` and `merge_clear_reports.py`.
- Local (Ollama) runs get a documented hardware-time **Cost proxy** so `C_norm`/CNA/CPS/CLEAR span
  the full model panel instead of only the two API-billed models.
- Fixed `risk_ratios` reading the deserialised dict `violation_vector` (previously `getattr`
  returned 0 for every dimension).

### Documentation

- Added a paper-ready System Architecture section (`docs/framework/paper-architecture.md`) with a
  rendered end-to-end pipeline flowchart (`docs/reference/architecture-diagram.html`/`.svg`).

### Real-data-grounded environments (Phase 1, 2026-06-11)

- New `env_m100_*` environment set grounded in the real CINECA Marconi100 (M100)
  ExaData dataset, built **alongside** the existing envs (none modified). Hybrid grounding:
  real M100 metric vocabulary + values sampled from real M100 distributions + controlled,
  labeled scenario perturbations so ground truth stays authorable.
  - `env_m100_01` — GPU thermal hotspot (ipmi `gpu3_core_temp` ramps to ~88°C on r3n7)
  - `env_m100_02` — node power anomaly (ipmi `total_power` ~1400W on r10n4 vs ~644W baseline)
  - `env_m100_03` — rack cooling fault (rack-4 `ambient` rises to ~32°C on all nodes)
  - `env_m100_04` — node down (`r7n2` telemetry stops ~10:45 UTC + SLURM `down`)
  - `env_m100_05` — job failure correlation (`r2n5` `total_power` collapse at FAILED time)
  - `env_m100_06` — **real OOM**: anchored on an actual ExaData `OUT_OF_MEMORY` job (66353)
    with real `ganglia_pub` `mem_free` exhaustion (~270→8 GB vs ~315 GB total) on `r5n3`
  - All six pass the full F1–F7 fidelity gate; power kept in the telemetry parquet so F4 skips.
- Non-IPMI metric coverage: `scripts/build_m100_reference.py --long-metrics-dir` fits
  distributions from long-format metrics extracted from a `raw/` tar on `n1` and merges them
  into the committed reference (111 metrics total): `ganglia_pub` (`mem_free`, `mem_total`,
  `cpu_user`, `Gpu0_gpu_utilization`), `vertiv_pub` (`Supply_Air_Temperature`,
  `Return_Air_Temperature`), `nagios_pub` (`state`). `env_m100_03` now models a real causal
  chain: a `vertiv` CRAC `Supply_Air_Temperature` rise (~18→30°C) driving the rack `ambient`
  rise — mixing `ipmi_pub` + `vertiv_pub` telemetry.
- Telemetry uses M100 conventions inside the canonical schema: `r{rack}n{slot}` node names,
  real IPMI metric names, and an extra `plugin` column (`ipmi_pub`) for provenance.
- Distributions fit across a **population of 120 real M100 nodes** (from the full ExaData
  `time_aggregated/` dataset, 858 nodes / 24 GB on the `n1` server), not a single node —
  including a per-metric cross-node baseline spread (`node_baseline_std`) so each env node
  gets its own real baseline (e.g. rack-10 peers span ~530–720 W).

### Tooling

- `scripts/build_m100_reference.py` — fits per-metric distributions either from a real
  node **population** (`--aggregated-dir` over `time_aggregated/`, run on `n1`) or the single
  bundled sample (`--sample`, offline fallback) → committed
  `benchmark/environments/_m100_reference/` (`metric_distributions.json`, `metric_map.md`).
  The committed reference covers 104 real IPMI metrics from 120 nodes.
- `scripts/build_m100_bundles.py` — deterministic importer (byte-identical rebuild). Adds a
  `--real-baselines <time_aggregated/>` mode that takes each env node's baseline from a real
  M100 node's actual trace at the env's real timestamp (verified on `n1`); the offline
  distribution-sampled build stays canonical/scored. A `--relative-anomalies` flag (default off,
  so the canonical build is byte-identical) scales upward magnitude anomalies to each node's real
  baseline, so in real-baseline mode the injected anomaly stays a clear outlier above noisy real
  peer load (env_02 spike ≈ 2.4× the busiest real peer). Also an optional `--dataset-path`
  live-slice refinement that gracefully no-ops without the full dataset.

### Real job grounding

- `scripts/build_m100_jobs.py` extracts a curated pool of **real anonymized M100 job records**
  from the `job_table` plugin (`job_info_marconi100`) → committed
  `_m100_reference/real_jobs.json` (~84 records, 12 per state). Real `job_state` carries genuine
  terminal states (`COMPLETED`, `FAILED`, `OUT_OF_MEMORY`, `NODE_FAIL`, `TIMEOUT`, `CANCELLED`,
  `PREEMPTED`), real `partition`/`qos`/`user_id`/`num_cpus`/walltimes; durations derived from
  `end_time - start_time` (`run_time` is null in the dataset).
- `build_m100_bundles.py` appends real records as queue context to each env (`--real-jobs`,
  default on; `--no-real-jobs` to disable). Scenario anchor jobs are preserved and job counts
  stay <8, so the fidelity gate is unaffected. Builds offline from the committed pool.

### Schema

- `SlurmJob` extended with optional M100 `job_info_marconi100` fields (`qos`, `job_state`,
  `derived_ec`, `run_time`, `time_limit`, `priority`, `state_reason`, `nodes`,
  `min_memory_cpu/node`, `eligible_time`) — additive, all existing bundles validate unchanged.

### Tasks

- 8 new dev-split tasks: `M100_MON_SYS_001/002`, `M100_MON_USR_001`,
  `M100_ENERGY_SYS_001`, `M100_ENERGY_FAC_001/002`, `M100_JOB_USR_001/002`
  (MON/ENERGY/JOB × sysadmin/scientific_user/facility_admin).
  `dataset_splits.py` / frozen test split untouched.

### Docs & tests

- `docs/guides/m100_environments.md` and per-env `provenance.json` (grounding rationale and
  fidelity-gate handling).
- New tests: importer determinism/clamp bounds, `SlurmJob` back-compat, fidelity-gate-enabled
  env load, end-to-end task scoring (61 pass).
- `aobench validate benchmark` → 88 tasks / 29 environments, passes.

## v0.3 dataset integrity (2026-05-03)

### Dataset

- 80 task specs across 10 QCATs × 5 roles (up from 71 in MASTER.md snapshot)
- Dataset split frozen at **62 dev / 18 test** (~22% held-out) in `benchmark/tasks/dataset_splits.py`
- Fixed 16 `benchmark_split` mismatches between JSON spec files and `dataset_splits.py`
- Added missing `validation_status` field to 15 AIOPS / PERF / SEC specs (`"not_started"`)

### Environment fidelity

- env_07 and env_12 now pass all F1–F7 fidelity checks (were failing F1/F2/F3 due to
  synthetic slurm data with uniform runtimes and no completed jobs)
- Added historical COMPLETED jobs with realistic lognormal runtime distributions to both envs
- All 23 environment snapshot bundles now pass `aobench validate snapshots` (23/23)

### Validation

- `aobench validate benchmark` → 80/80 tasks, 26/26 environments, passes without `AOBENCH_SKIP_FIDELITY`
- Added three new stub environments (env_24 CUDA/OpenMPI conflict, env_25 privilege escalation, env_26 IB link flapping) with complete bundles

---

## v0.1.0 (2026-05-01)

First public release.

### Dataset

- 30 original HPC operational tasks across a 3×3 role–QCAT grid (JOB × 10, MON × 10, ENERGY × 10)
- 36 HPC task set v1 tasks (job_ops, node_ops, telemetry, energy, dataflow, RBAC)
- 20 deterministic HPC environment snapshot bundles (env_01–env_20) covering 8 scenario types (v0.1 baseline; expanded to env_01–env_26 in v0.3)
- Difficulty tiers: 10 easy / 13 medium / 7 hard across original 30 tasks
- Dataset splits frozen (70% dev, 30% test, stratified by QCAT × role)
- AOBench-Lite 3-stage selection pipeline (SWE-bench Lite methodology)

### Mock HPC Environment

- 5 tool families: SLURM, docs, RBAC, telemetry, facility
- 16 tool methods catalogued in `benchmark/configs/hpc_tool_catalog.yaml`
- RBAC policy v1.1: 5 roles, forbidden-call hard-fail, per-environment `rbac_policy.yaml`

### Scoring

- 6 evaluation dimensions: Outcome, Tool-Use (BFCL-decomposed), Grounding, Governance, Efficiency, Robustness
- CLEAR five-dimension scorecard (E/A/R/CNA/CPS)
- Completion-under-Policy (CuP) metric for RBAC compliance
- pass^k reliability metric with 5 trials per task
- HPC error taxonomy: 14 categories with auto-detect and LLM-judge annotation
- Hybrid scorer: deterministic (DAComp three-tier) + rubric (LLM-judge) paths
- Scoring profiles: `alpha0_minimal`, `alpha1_grounding`, `default_hpc_v01`

### Adapters

- `direct_qa`: zero-tool baseline
- `openai`: GPT-4o, GPT-4o-mini, o1-mini via OpenAI or Azure OpenAI
- `anthropic`: Claude Sonnet, Claude Opus
- `mcp`: stdio and SSE transports

### CLI

- `aobench validate benchmark` — validate all task and environment data
- `aobench run task / run all` — run evaluations with configurable adapter, split, verbosity
- `aobench report json / html / slices` — generate result reports
- `aobench compare` — diff two run directories
- `aobench robustness task / robustness all` — compute pass^k reliability
- `aobench clear run` — CLEAR scorecard for a run
- `aobench lite select` — AOBench-Lite subset selection

### Infrastructure

- Langfuse observability integration (`--langfuse` flag)
- GitHub Actions CI: lint + typecheck + tests + benchmark validation on every push
- 534 unit and integration tests
- Apache 2.0 license
