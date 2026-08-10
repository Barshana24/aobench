---
title: "AOBench glossary — QCAT, CFS, CLEAR, pass^k, trace, snapshot"
description: "Definitions of every AOBench term: QCAT, role, environment snapshot, trace, gold trajectory, hard fail, CFS, CLEAR, pass^k, WorfEval, BFCL decomposition, fidelity gate, and more."
keywords:
  - AOBench glossary
  - QCAT definition
  - pass^k
  - CLEAR scorecard
  - cascading failure score
---

# Glossary

Terms as AOBench uses them. Where a term is borrowed from the literature, the source is
named so you can check we are using it the same way.

## Benchmark structure

**Task** — one operational question asked by one role about one environment, together
with its gold answer, gold trajectory, evaluation criteria, and RBAC metadata. Stored
as JSON under `benchmark/tasks/specs/`. See the
[task catalog](task-catalog.md).

**QCAT (question category)** — the operational domain a task belongs to. AOBench has
ten: `JOB`, `MON`, `ENERGY`, `PERF`, `DATA`, `SEC`, `FAC`, `ARCH`, `AIOPS`, `DOCS`.
List them with `aobench list qcats`.

**Role** — who is asking. Five: `scientific_user`, `sysadmin`, `facility_admin`,
`researcher`, `system_designer`. The role determines both what a correct answer looks
like and which tools the agent is permitted to call. The same question asked by two
roles is two different tasks with two different right answers.

**Environment snapshot bundle** — a directory of frozen files representing a cluster at
a moment in time: Slurm state, telemetry, documentation, RBAC policy, incident
metadata. The unit of reproducibility. See the
[environment catalog](environment-catalog.md).

**Grounded environment** — a bundle built from real operational data rather than
authored. AOBench's six grounded bundles come from the public Marconi100 ExaData
release.

**Split** — `dev` (67 tasks, open) or `test` (21 tasks, locked behind
`AOBENCH_UNLOCK_TEST=1`). Report which one you used.

**AOBench-Lite** — a curated subset for fast iteration, defined in
`benchmark/tasks/lite_manifest_v1.json` and run with `aobench lite`.

**AOBench-QA** — ~95 HPC operational queries with role-specific variants, shipped in
`benchmark/qa/`. Seeds task design and drives the `direct_qa` baseline.

## Execution

**Adapter** — the shim that turns "an agent" into something AOBench can run. Four ship
with the project: `direct_qa`, `openai`, `anthropic`, `mcp`. Implementing
`BaseAdapter.run(context) -> Trace` is how you evaluate your own system.

**`direct_qa`** — the tool-free reference baseline. Answers from the prompt alone,
calls nothing. Its score is the floor a real agent must beat, not a target.

**Tool registry** — the role-filtered set of tools an agent is offered for a task,
constructed from the environment's `rbac_policy.yaml`. An agent never sees a tool its
role may not use; attempts to call one anyway are governance violations.

**Trace** — the ordered record of everything that happened during a run: each tool
call, its arguments, its result, and each agent message. The object that gets scored.

**Gold trajectory** — the ordered tool calls a competent operator would make. Used by
the tool-use dimension; an agent is not required to match it exactly, but large
divergence costs.

**Gold evidence references** — the specific facts in the bundle that support the gold
answer. Used by the grounding dimension.

**Execution context** — task + environment + tool registry + run ID, handed to an
adapter as its entire world.

## Scoring

**Dimension** — one scored axis. AOBench has seven weighted ones: `outcome`,
`tool_use`, `grounding`, `governance`, `robustness`, `efficiency`, `workflow`.

**Weight profile** — a named set of dimension weights summing to 1.0, from
`benchmark/configs/scoring_profiles.yaml`. `default_hpc_v01` is the standard. Always
report which profile produced a number: `aobench list profiles`.

**Aggregate score** — the weighted sum of the dimension scores, in [0, 1].

**Hard fail** — a violation that zeroes the aggregate score regardless of every other
dimension. An RBAC breach is the canonical case. There is no partial credit for
overstepping a role.

**Deterministic scoring path** — tasks scored by exact, numeric, or set matching, via
`HybridScorer`. Exactly reproducible; no model in the loop.

**Rubric scoring path** — tasks scored by an LLM judge against a structured rubric.
Necessary for open-ended answers, and a source of variance — see
[limitations](../about/limitations.md).

**GSB (Good–Sufficient–Bad)** — a coarse three-level judgement optionally combined with
the rubric score using weight `alpha`.

**Component spec** — one checkable sub-claim of a deterministic task. A task's score is
built from its components rather than from one all-or-nothing comparison.

**CFS (Cascading Failure Score)** — the propagation of a failed component's penalty to
the components that depend on it, via `upstream_deps`. If an agent misidentifies the
failing node, everything it concludes downstream is wrong *because of that*, and CFS
stops the task from collecting partial credit for confidently-wrong follow-through.

**BFCL decomposition** — the tool-use dimension is decomposed the way the Berkeley
Function Calling Leaderboard decomposes calls (function selection, argument
correctness, types), so AOBench tool-use numbers are interpretable alongside that
literature.

**WorfEval / `workflow` dimension** — compares the workflow DAG the agent actually
executed against the task's `ground_truth_workflow` via sub-graph matching. Only
contributes when a task defines a gold workflow.

**pass^k** — the probability of succeeding on *all* k independent attempts. Distinct
from pass@k (at least one success). AOBench uses pass^k because an operator that is
right four times in five is not a safe operator. Measured by
`aobench robustness task --n k`.

**CLEAR scorecard** — a whole run aggregated into five axes: **E**fficacy,
**A**ssurance, **R**eliability, **C**ost, **L**atency. One comparable number per
model. Produced by `aobench clear run`.

**Engagement-aware governance** — governance is graded by whether the agent actually
engaged with the task, so an agent that refuses everything cannot farm a perfect
governance score by never acting.

## Data quality

**Fidelity gate (F1–F7)** — internal-consistency checks a task and its environment must
pass: the anomaly a task asks about must actually be present in the telemetry, the gold
evidence must exist in the bundle, and so on. Bypassable with
`AOBENCH_SKIP_FIDELITY=1` (which the test suite sets, to keep unit tests fast).

**Contamination risk** — a per-task field flagging how likely the task is to have
leaked into model training data. Mitigated but not solved by the locked test split.

**Provenance** — for grounded bundles, the `provenance.json` record of which ExaData
window the snapshot came from and what transformation was applied.

**Error taxonomy** — a 24-leaf classification of agent failure modes, adapted from
TRAIL, in `benchmark/configs/error_taxonomy.yaml`. Used by the error annotator to say
*how* an agent failed, not just that it did.

## External terms

**ExaData** — CINECA's public release of operational data from Marconi100, the source
of AOBench's six grounded environments.

**Marconi100 (M100)** — CINECA's 980-node IBM Power9 + V100 Tier-0 supercomputer,
decommissioned in 2026 and the subject of ExaData.

**Slurm** — the workload manager used on most HPC systems, and the model for AOBench's
mock scheduler tool.

**RBAC** — role-based access control. In AOBench, the per-environment policy that
decides which tools each role may call.

**MCP (Model Context Protocol)** — the open protocol AOBench uses both to evaluate
external agents (the `mcp` adapter) and to expose itself as a server
(`aobench serve mcp`).

**A2A (Agent2Agent)** — the agent-interoperability protocol whose Agent-Card
conformance, delegation, and attribution properties AOBench scores.

**Langfuse** — the observability backend AOBench exports traces to.

---

*Missing a term? [Open an issue](https://github.com/MSKazemi/aobench/issues/new/choose) —
a glossary gap is a documentation bug.*
