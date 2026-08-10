# Contributing to AOBench

## Setup

```bash
git clone https://github.com/MSKazemi/aobench
cd aobench
make install        # creates .venv and installs all deps
make validate       # verifies benchmark data loads cleanly
make test           # ~1510 tests should pass
```

Requires [uv](https://github.com/astral-sh/uv). Python 3.11+.

If `make` is unavailable, the equivalent commands are:

```bash
uv sync --all-extras
uv run aobench validate benchmark
uv run python -m pytest tests/
```

These are the same commands CI runs. Before opening a PR, also run:

```bash
uv run ruff check src tests
uv run ruff format src tests
uv run mypy src/aobench       # advisory — not all findings block a PR
```

---

## What to expect from us

- **First response within 3 working days.** A first response may just be "seen,
  I'll look properly on Friday" — that still counts, and you will get one.
- If a PR of yours goes quiet for more than a week, ping it. That is a
  maintainer failure, not rudeness on your part.
- **Prefer PRs under ~300 changed lines.** Larger work is welcome, but open an
  issue first so we can agree the approach before you write it.
- **Open an issue before starting** anything that changes the task schema, the
  scoring weights, the RBAC model, or a public CLI signature. Bug fixes, docs,
  tests, examples and new CLI flags need no prior discussion — just send them.
- **If an issue turns out to be already done, say so.** It happens — three of ours
  were. Flagging it is a real contribution and gets credited in `AUTHORS.md`; it is
  never something you should feel awkward about raising.

---

## Using AI assistance

**AI assistance is welcome.** We are not going to ask how you wrote your code, and
"you used an LLM" is not a rejection reason here — it would be a strange one in a
project about evaluating AI agents.

What we do ask is the same thing we would ask of any contributor:

- **You understand the change and can explain it in review.** If a reviewer asks
  "why this approach rather than X?", you should be able to answer.
- **You have run the tests locally.** `make check`, not "it looked right".
- **You take responsibility for it.** Your name is on the PR.
- **Please disclose substantial AI assistance in the PR description.** It costs you
  nothing, it is not held against you, and it helps us review well.

If you are pointing a coding agent at this repository,
[`AGENTS.md`](https://github.com/MSKazemi/aobench/blob/main/AGENTS.md) is
written for it — architecture, commands, invariants, and what must not be changed.
Point the agent there first.

---

## How to Add a Task

A task is a JSON file in `benchmark/tasks/specs/`. Every task must reference a real environment bundle and have a verified gold answer before it can be marked `scoring_readiness: ready`.

**Step 1 — Pick an environment.** Check which environments exist:

```bash
make coverage-matrix
ls benchmark/environments/
```

**Step 2 — Write the task spec.** Create `benchmark/tasks/specs/<TASK_ID>.json`:

```json
{
  "task_id": "JOB_USR_004",
  "title": "Short title",
  "query_text": "The exact question the agent will be asked.",
  "role": "scientific_user",
  "qcat": "JOB",
  "difficulty": "easy",
  "environment_id": "env_01",
  "gold_evidence_refs": ["slurm/job_details.json#oom_evidence"],
  "expected_answer_type": "diagnosis",
  "eval_criteria": {
    "evaluation_mode": "semantic_match",
    "gold_answer": "The exact correct answer derived from the environment data.",
    "required_evidence_refs": ["slurm/job_details.json#oom_evidence"]
  },
  "allowed_tools": ["slurm", "docs"],
  "hard_fail_conditions": [],
  "aggregate_weight_profile": "alpha1_grounding",
  "benchmark_split": "dev",
  "validation_status": "in_review",
  "scoring_readiness": "ready"
}
```

Valid values:
- `role`: `scientific_user` | `sysadmin` | `facility_admin`
- `qcat`: `JOB` | `MON` | `ENERGY`
- `difficulty`: `easy` | `medium` | `hard` | `adversarial`
- `evaluation_mode`: `semantic_match` | `exact_match` | `numeric_tolerance`
- `aggregate_weight_profile`: `alpha1_grounding` (recommended) | `alpha0_minimal` | `default_hpc_v01`
- `allowed_tools`: any subset of `["slurm", "docs", "rbac", "telemetry", "facility"]`

**Step 3 — Verify the gold answer** by reading the actual environment files in `benchmark/environments/<env_id>/`. The gold answer must be derivable from those files alone.

**Step 4 — Validate:**

```bash
make validate
uv run python scripts/check_coverage.py
```

**Step 5 — Run a baseline:**

```bash
make run TASK=JOB_USR_004 ENV=env_01 ADAPTER=direct_qa
```

---

## How to Add an Environment

An environment is a directory under `benchmark/environments/env_XX/` with deterministic snapshot data.

**Required files:**

```
env_XX/
  metadata.yaml      # environment_id, scenario_type, supported_roles, included_files, ...
  manifest.txt       # list of all data files (one per line)
  policy/
    rbac_policy.yaml # role permissions
```

**Optional data directories** (add whichever apply to your scenario):

| Directory | Contents |
|-----------|----------|
| `slurm/` | `slurm_state.json`, `job_details.json`, `pending_jobs.json`, `qos_limits.json` |
| `telemetry/` | `node_metrics.json`, `memory_events.csv`, `queue_pressure_metrics.csv` |
| `power/` | `node_power_*.csv`, `cluster_energy_*.csv`, `rack_energy_*.csv` |
| `rack/` | `rack_telemetry_*.csv` |
| `inventory/` | `node_map.csv`, `rack_layout.csv` |
| `docs/` | Markdown policy/guide files for the `docs` tool |
| `incidents/` | `incident_metadata.json` |
| `cooling/` | `crac_status.json` |
| `alerts/` | `node_alerts.json` |

See `benchmark/environments/env_01/` (simple) or `env_05/` (facility scenario) as templates.

Validate after creating: `make validate`

---

## How to Add an Adapter

An adapter wraps an LLM (or any agent) and translates AOBench's `ExecutionContext` into a `Trace`.

**Step 1 — Create the adapter file:**

```python
# src/aobench/adapters/my_adapter.py
from aobench.adapters.base import BaseAdapter
from aobench.runners.context import ExecutionContext
from aobench.schemas.trace import Trace

class MyAdapter(BaseAdapter):
    name = "my_adapter"

    def run(self, context: ExecutionContext) -> Trace:
        # 1. Use context.task.query_text as the user prompt
        # 2. Use context.tools.call(tool_name, method, **kwargs) for tool calls
        # 3. Build and return a Trace with steps, final_answer, hard_fail, etc.
        ...
```

Key objects:
- `context.task` — `TaskSpec` (query, role, allowed_tools, gold_evidence_refs)
- `context.tools` — `ToolRegistry` (call tools, check permissions)
- `context.tools.available_tool_names` — list of tool names available for this task/role
- Return a `Trace` — see `src/aobench/schemas/trace.py`

**Step 2 — Register in `run_cmd.py`:**

```python
# src/aobench/cli/run_cmd.py  — _build_adapter()
if name == "my_adapter":
    from aobench.adapters.my_adapter import MyAdapter
    return MyAdapter()
```

**Step 3 — Add OpenAI-style tool schemas** (if the adapter uses function calling):

Add your tool's JSON schema to `src/aobench/adapters/openai_adapter.py:_TOOL_SCHEMAS` — or generate it from the tool class if it exposes a `schema()` method.

**Step 4 — Test:**

```bash
make run TASK=JOB_USR_001 ENV=env_01 ADAPTER=my_adapter
```

---

## How to Add a Scorer

A scorer evaluates one dimension of agent quality from a `TaskSpec` and `Trace`.

```python
# src/aobench/scorers/my_scorer.py
from aobench.schemas.task import TaskSpec
from aobench.schemas.trace import Trace
from aobench.scorers.base import BaseScorer, ScorerOutput

class MyScorer(BaseScorer):
    dimension = "my_dimension"

    def score(self, task: TaskSpec, trace: Trace) -> ScorerOutput:
        if trace.hard_fail:
            return ScorerOutput(dimension=self.dimension, score=0.0,
                                hard_fail=True, hard_fail_reason=trace.hard_fail_reason)
        score = ...  # compute 0.0–1.0
        return ScorerOutput(dimension=self.dimension, score=score, notes="...")
```

Register in `src/aobench/scorers/aggregate.py:_SCORERS` and add the dimension to `DimensionScores` in `src/aobench/schemas/result.py`. Add a weight entry to each profile in `benchmark/configs/scoring_profiles.yaml`.

Write tests in `tests/unit/test_my_scorer.py`.

---

## Code Standards

- Python 3.10+ (3.12 in CI and Docker), Pydantic v2, Typer CLI
- `uv run ruff check src/ tests/` must pass (no errors)
- `uv run mypy src/aobench/` must pass
- Every new module needs at least basic unit tests
- Run `make check` before opening a PR

## Branch and PR Conventions

- Branch from `main`, name: `feature/<topic>` or `fix/<topic>`
- Each PR should do one thing
- The CI workflow (`.github/workflows/ci.yml`) must pass

## License and sign-off

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.

**There is no CLA.** AOBench uses a [Developer Certificate of Origin](DCO.md) — the same one the Linux
kernel uses. There is nothing to sign, no account to create, and nothing for your employer's legal team
to review. You simply certify that you wrote the change and are allowed to submit it, by adding one
line to your commit:

```
Signed-off-by: Your Name <your.email@example.com>
```

Git writes it for you with `-s`:

```bash
git commit -s -m "your message"
```

Forgot it? `git commit --amend --signoff && git push --force-with-lease`. Want it always on?
`git config --global format.signOff true`.

**You keep the copyright in your work.** AOBench is Apache-2.0 and stays that way.
