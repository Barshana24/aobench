# Reproducing results

A benchmark number that cannot be re-derived is an assertion, not evidence. This page states
what AOBench pins, what it cannot pin, and how to re-run a published result.

## What is deterministic, and what is not

| Component | Deterministic? | Why |
|---|---|---|
| Environment snapshots | **Yes** | Frozen directory bundles with a recorded manifest. The same snapshot returns the same tool responses on every run |
| Mock tools (SLURM, telemetry, docs, RBAC, facility) | **Yes** | They read from the snapshot; no network, no clock dependence |
| Task specs and gold trajectories | **Yes** | Versioned JSON, changed only by a tagged release |
| Deterministic scoring path | **Yes** | Exact / numeric / set matching over the trace |
| **The model under test** | **No** | A hosted model is not a fixed artifact. Providers update weights and serving behaviour without notice, and sampling is stochastic |
| **Rubric (LLM-judge) scoring path** | **Partially** | Pinned by judge model, prompt, and a content hash of the rubric — but inherits the model non-determinism above |

This is the honest boundary: **AOBench pins everything on its side of the interface.** It
cannot pin the model, and no benchmark can. That is why the reliability probe exists and why
a single run should not be reported as a point estimate without qualification.

## What identifies a run

Four things, and all four belong in any paper, table, or issue that reports a score:

1. **Version tag** of AOBench — e.g. `v0.4.0`
2. **Scoring profile** — e.g. `default_hpc_v01`
3. **Split** — `dev` or `test`
4. **Adapter and model** — e.g. `openai:gpt-4o`, or `direct_qa` for the zero-tool baseline

Every run directory records these in its manifest, along with the snapshot hashes, so a
result carries its own provenance.

## Re-running a result

```bash
# 1. Check out the exact version the result came from
git clone https://github.com/MSKazemi/aobench && cd aobench
git checkout v0.4.0

# 2. Install
uv sync --all-extras

# 3. Confirm the corpus loads intact before trusting anything downstream
uv run aobench validate benchmark      # expects 88 tasks / 29 environments

# 4. Re-run
uv run aobench run all --adapter direct_qa --split dev

# 5. Score and report
uv run aobench report json data/runs/<run_id>
uv run aobench clear run data/runs/<run_id>
```

The `direct_qa` adapter needs no API key and no network, so **step 4 is fully reproducible
on any machine**. It is the right baseline to check your setup against before spending money
on a hosted model.

## The held-out test split

The `test` split is locked behind an environment variable and is intended to be run **once**,
after all development-split analysis is finished:

```bash
AOBENCH_UNLOCK_TEST=1 uv run aobench run all --adapter <adapter> --split test
```

The lock is a speed bump against accidental use, not a security control. The discipline it
protects — not tuning against the test split — is yours to keep. If you run test more than
once, say so when you report the number.

## Comparing two runs

```bash
uv run aobench compare runs <run_a> <run_b>
```

Two scores are not different because one is larger. AOBench reports bootstrap confidence
intervals, and overlapping intervals mean the comparison is unresolved — report it that way.
For repeated-run reliability, `aobench robustness task` computes the unbiased pass^k
estimator over N repeats.

## If your numbers differ

In rough order of likelihood:

1. **Different version.** Check `git describe --tags`. The corpus grew from 80 to 88 tasks and 26 to 29 environments; scores are not comparable across that boundary.
2. **Different scoring profile.** Dimension weights differ; the aggregate changes even though the per-dimension scores don't.
3. **Different split.** Dev and test are different task sets.
4. **The provider changed the model.** The most common cause for hosted models, and the hardest to detect. Pin an explicitly dated model identifier where the provider offers one.
5. **A modified snapshot.** `aobench validate benchmark` will catch this.

If none of these explain it, that is worth an [issue](https://github.com/MSKazemi/aobench/issues) — a reproducibility gap is a bug.

## Known limitations

Stated plainly, because a benchmark that hides these is not usable as evidence:

- **23 of 29 environments are synthetic**, fidelity-validated against reference distributions rather than recorded from a live system. Six are grounded in real Marconi100 ExaData.
- **The action space is read-only and advisory.** AOBench does not test destructive operations, so it does not tell you whether an agent is safe to give write access.
- **Mock tools are not a cluster.** Fidelity is validated at the level of data distributions and interfaces, not real system dynamics under load.
- **Rubric-scored tasks inherit judge-model variance.** They are pinned by prompt and content hash, not made deterministic.

See [Cite AOBench](citation.md) for what to report alongside a result.
