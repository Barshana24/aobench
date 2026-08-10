---
title: "Run AOBench in CI — gate your agent on a benchmark score"
description: "How to use AOBench as a regression gate in GitHub Actions or GitLab CI: pin a version, choose a deterministic subset, set a threshold, and fail the build when an agent regresses."
keywords:
  - benchmark in CI
  - agent regression test
  - GitHub Actions LLM evaluation
---

# Running AOBench in CI

AOBench is deterministic on the deterministic scoring path, which makes it usable as a
regression gate: change a prompt, change a model, change your planner — and find out in
CI whether your agent got worse.

## The three rules

1. **Pin the AOBench version.** Never a floating range — the corpus is part of the
   version; see [versioning](../about/versioning.md). AOBench is not on PyPI yet, so
   today that means pinning the tag rather than `pip install aobench==0.4.1`:

    ```bash
    pip install "git+https://github.com/MSKazemi/aobench@v0.4.1"
    ```
2. **Pin the model snapshot.** `gpt-4o-2024-11-20`, not `gpt-4o`. A provider updating
   an alias will otherwise look exactly like a regression in your code.
3. **Use a fixed subset, and avoid rubric-scored tasks in the gate.** A judge model in
   the loop makes the gate flaky, and a flaky gate gets disabled within a month.

## GitHub Actions

```yaml
name: agent-benchmark

on:
  pull_request:
  schedule:
    - cron: "0 4 * * 1"    # weekly full run

jobs:
  aobench:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: astral-sh/setup-uv@v9.0.0
        with:
          python-version: "3.12"

      - name: Install AOBench (pinned)
        run: uv pip install --system "aobench==0.4.1"

      - name: Sanity-check the install
        run: aobench doctor

      - name: Run the gate subset
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          aobench run all \
            --adapter "mcp:stdio:python my_agent/server.py" \
            --split dev \
            --qcat JOB,SEC \
            --output data/runs

      - name: Enforce the threshold
        run: python ci/check_score.py data/runs --min-score 0.62 --max-hard-fails 0

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: aobench-traces
          path: data/runs/
```

Uploading the traces matters: when the gate fails, the trace is what tells you *why*,
and a failed CI run with no artifact is just a red X.

## The threshold script

`examples/04_ci_gate.py` in the repository is a working version of this. The shape:

```python
import json, sys
from pathlib import Path

run_dir = Path(sys.argv[1])
summary = json.loads(next(run_dir.rglob("run_summary.json")).read_text())

score = summary["aggregate_score"]
hard_fails = sum(1 for r in summary["results"] if r["hard_fail"])

print(f"aggregate={score:.4f}  hard_fails={hard_fails}")

if hard_fails:
    sys.exit(f"FAIL: {hard_fails} RBAC hard-fail(s) — not acceptable at any score")
if score < MIN_SCORE:
    sys.exit(f"FAIL: {score:.4f} < {MIN_SCORE}")
```

## Choosing a threshold

Do not invent one. Measure your agent's current score over three runs, take the lowest,
and subtract a small margin:

```bash
for i in 1 2 3; do aobench run all --adapter my_agent --split dev --qcat JOB; done
```

Then **ratchet**: when the score improves durably, raise the floor. A threshold that
never moves stops being informative.

## Gate on hard fails separately, and at zero

An RBAC hard fail should fail the build regardless of the aggregate score. It is a
different class of event from "slightly worse at diagnosis", and averaging it into a
single number hides exactly the thing you most want CI to catch.

## Keeping it cheap

| Technique | Effect |
|---|---|
| `aobench lite` | Curated fast subset instead of the full split |
| `--qcat JOB,SEC` | Only the categories your agent actually targets |
| `direct_qa` on every PR, real model weekly | Catches structural breakage for free |
| Cache the uv environment | Removes install time from every run |

The `direct_qa` trick is underrated: running the tool-free baseline on every PR costs
nothing and still catches "the adapter no longer loads" and "the tool registry broke",
which is most of what breaks.

## GitLab CI

```yaml
aobench:
  image: python:3.12
  script:
    - pip install "aobench==0.4.1"
    - aobench doctor
    - aobench run all --adapter my_agent --split dev --qcat JOB
    - python ci/check_score.py data/runs --min-score 0.62 --max-hard-fails 0
  artifacts:
    when: always
    paths: [data/runs/]
```

## Reproducibility in CI

Set these so a CI number means the same thing as a local one:

```bash
AOBENCH_BENCHMARK_ROOT   # only if you use a custom corpus
AOBENCH_SKIP_FIDELITY    # leave UNSET in CI; it weakens the corpus checks
AOBENCH_UNLOCK_TEST      # leave UNSET; never gate on the held-out split
```

Gating on the test split defeats the purpose of holding it out: after a few months of
ratcheting against it, you have tuned on it.
