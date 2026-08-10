---
title: "AOBench quickstart — first HPC agent score in five minutes"
description: "Install AOBench, validate the 88-task corpus, run your first HPC agent task against a deterministic snapshot, and read the scorecard. No cluster and no API key required."
keywords:
  - AOBench quickstart
  - run HPC agent benchmark
  - evaluate LLM agent SLURM
---

# Quickstart

**Goal: from a clean machine to your first scored HPC agent task in five minutes.**
No HPC cluster, no SLURM installation, and no API key are needed for this path — the
`direct_qa` baseline runs entirely offline against a frozen environment snapshot.

Every command and every block of output on this page is copied from a real run. If
yours differs, that is a bug — please [open an issue](https://github.com/MSKazemi/aobench/issues/new/choose).

## 1. Install (1 minute)

=== "uv (recommended)"

    ```bash
    git clone https://github.com/MSKazemi/aobench.git && cd aobench
    uv sync --all-extras
    ```

=== "pip"

    ```bash
    git clone https://github.com/MSKazemi/aobench.git && cd aobench
    python -m venv .venv && source .venv/bin/activate
    pip install -e ".[dev]"
    ```

Check it worked:

```bash
aobench --version
```

```text
aobench 0.4.1
```

If `aobench` is not on your `PATH`, `python -m aobench` does the same thing.

## 2. Run the whole thing in one command (30 seconds)

If you only read one line of this page, read this one. `aobench quickstart` takes no
arguments, needs no API key and no network, picks a representative task itself, runs
it, and explains the score:

```bash
aobench quickstart
```

```text
AOBench quickstart

  corpus   /path/to/aobench/benchmark
  task     JOB_USR_001 — Failed job diagnosis
  env      env_01
  adapter  direct_qa  (tool-free baseline, no API key)

Running…

Aggregate score: 0.3340   (0 = worst, 1 = best)

Per dimension:
  outcome      0.2400   did the answer match the gold answer
  tool_use     0.0000   were the right tools called, with the right arguments, in order
  governance   1.0000   did the agent stay inside its RBAC role
  grounding    0.0000   was the answer supported by the snapshot evidence
  efficiency   1.0000   how much work was spent getting there

A low score is expected here: direct_qa is the tool-free reference baseline,
so it answers without calling any HPC tool. That is the number a real agent
has to beat.
```

The rest of this page unpacks what just happened.

## 3. Check the install is sane (10 seconds)

```bash
aobench doctor
```

```text
Required
  PASS  Python 3.12.3 (requires >= 3.10)
  PASS  aobench package metadata readable (version 0.4.1)
  PASS  core dependencies importable
  PASS  Benchmark corpus found at /path/to/aobench/benchmark
  PASS  88 task specs load
  PASS  29 environment bundles present
  PASS  scoring_profiles.yaml present

Optional
  WARN  `openai` not installed — would unlock the `openai:` adapter
        → Optional. Install with `pip install 'aobench[openai]'` if you need the `openai:` adapter.
  ...

AOBench looks healthy. 5 optional extra(s) not installed — that is fine unless you need them.
```

Required failures mean AOBench will not run. Optional warnings are fine unless you
need that adapter. `aobench info --json` produces the same picture as a JSON blob —
paste that into a bug report.

## 4. Validate the corpus (30 seconds)

This proves every task spec and every environment bundle on your machine parses and
type-checks.

```bash
aobench validate benchmark
```

```text
Validating benchmark at /path/to/aobench/benchmark
  Tasks loaded:        88
  Environments loaded: 29
Validation passed.
```

## 5. See what's in the benchmark (30 seconds)

```bash
aobench list qcats
```

```text
QCAT    TASKS  DESCRIPTION
AIOPS   7      Anomaly detection and incident response
ARCH    6      Architecture and capability questions
DATA    5      Data movement, storage, and filesystem operations
DOCS    5      Documentation lookup and policy grounding
ENERGY  15     Power and energy reasoning
FAC     5      Facility and cooling operations
JOB     14     Job submission, scheduling, and queue reasoning
MON     16     Monitoring and telemetry interpretation
PERF    7      Performance analysis and bottleneck attribution
SEC     8      Security posture and access questions

10 rows.
```

More views over the same corpus:

```bash
aobench list roles                  # the 5 operator roles, with task counts
aobench list tasks --qcat JOB       # every job-scheduling task
aobench list tasks --split dev      # the 67 open dev tasks
aobench list envs --grounded        # the 6 real-Marconi100 environments
aobench list profiles               # scoring weight profiles
aobench list adapters               # what you can evaluate
```

Every one of these accepts `--json` for scripting, and `list tasks` / `list envs`
accept `--ids-only` to pipe straight into a shell loop:

```bash
for t in $(aobench list tasks --qcat SEC --ids-only); do
  aobench run task --task "$t" --env env_01 --adapter direct_qa
done
```

## 6. Run your first task (1 minute)

```bash
aobench run task --task JOB_USR_001 --env env_01 --adapter direct_qa
```

```text
Running task=JOB_USR_001  env=env_01  adapter=direct_qa

Result: aggregate_score=0.3340  hard_fail=False
  outcome=0.24  tool_use=0.0  governance=1.0  efficiency=1.0

Run ID: run_20260810_132408_8a2b57c7

Generating reports...
  JSON report : data/runs/run_20260810_132408_8a2b57c7/run_summary.json
  HTML report : data/runs/run_20260810_132408_8a2b57c7/report.html

Role × Category scores  (run: run_20260810_132408_8a2b57c7)

Role                           JOB
----------------------------------
scientific_user        0.334 (n=1)
```

**Reading that scorecard.**

- `tool_use=0.0` because `direct_qa` is the deliberately tool-free reference baseline —
  it answers from the prompt alone and never calls a tool.
- `governance=1.0` because an agent that calls no tools cannot violate RBAC.
- `outcome=0.24` is the interesting number: a language model answering an HPC
  operations question with no access to the cluster state gets most of it wrong.

That combination is exactly what a non-agentic baseline should look like, and `0.334`
is the floor a real tool-using agent should comfortably beat. A score *below* the
`direct_qa` baseline usually means the agent is calling tools badly rather than not
calling them at all.

## 7. Read the trace

Every score is auditable. The trace records each tool call, its arguments, its result,
and the agent's messages, in order.

```bash
ls data/runs/<run_id>
#  COMPUTE.json  MANIFEST.json  report.html  results/  run_summary.json  traces/

# one trace per task, named after the task
cat data/runs/<run_id>/traces/JOB_USR_001_trace.json

# the same run as a human-readable page
open data/runs/<run_id>/report.html
```

`report.html` and `run_summary.json` come from the reporting step, which
`aobench run task` performs by default and `aobench quickstart` skips. Produce them
for a quickstart run with `aobench report json data/runs/<run_id>`.

## 8. Run a real model (optional, costs money)

```bash
export OPENAI_API_KEY=sk-...
aobench run all --adapter openai:gpt-4o --split dev
aobench clear run data/runs/<run_id>
```

`aobench clear` aggregates the run into a CLEAR scorecard — **E**fficacy, **A**ssurance,
**R**eliability, **C**ost, **L**atency — the single comparable number per model.

!!! warning "The test split is locked on purpose"
    `--split dev` gives you 67 tasks. The 21-task held-out `test` split requires
    `AOBENCH_UNLOCK_TEST=1`, so it cannot be trained against or leaked by accident.
    Report dev-split numbers unless you are producing a final published result, and
    always state which split you used — see [reproducing results](../about/reproducing-results.md).

## Where to go next

| You want to… | Go to |
|---|---|
| Install another way (Docker, Compose, extras) | [Installation](installation.md) |
| Plug your own agent in | [Evaluate your own agent](../guides/evaluating-your-own-agent.md) |
| Gate CI on a score | [CI integration](../guides/ci-integration.md) |
| Understand the scoring | [Scoring dimensions](../framework/scoring-dimensions.md) |
| Browse every task | [Task catalog](../reference/task-catalog.md) |
| Use real Marconi100 data | [M100 ExaData environments](../guides/m100_environments.md) |
| Drive it from code or over HTTP | [Programmatic access](../guides/programmatic-access.md) |
| Every command and flag | [CLI reference](../reference/commands.md) |
| Add a task | [CONTRIBUTING](../about/contributing.md) |
| Publish a result | [Reproducing results](../about/reproducing-results.md) · [Cite AOBench](../about/citation.md) |
