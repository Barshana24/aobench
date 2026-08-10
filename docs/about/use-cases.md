---
title: "AOBench use cases — who evaluates HPC agents, and why"
description: "Concrete use cases for AOBench: HPC centres screening operational agents, researchers studying tool use and governance, model developers, CI regression gates, and teaching HPC operations."
keywords:
  - HPC agent use cases
  - evaluate AI operator
  - agent governance evaluation
---

# Use cases

Five audiences, five different reasons to run this benchmark. Each section says what
to run and what a good outcome looks like.

## 1. An HPC centre deciding whether to let an agent near operations

**The question:** "A vendor says their agent can triage our job failures. Can it?"

**What to run:**

```bash
aobench run all --adapter mcp:stdio:<their agent> --split dev
aobench clear run data/runs/<run_id>
aobench report slice data/runs/<run_id> --by role
```

**What to look at:** the governance dimension first, and the hard-fail count. An agent
that scores well on outcome while hard-failing on RBAC is more dangerous than one that
scores badly on both, because it will look competent right up until it does something
it should not have been able to do.

**What a good result licenses:** further evaluation on your own snapshots. Not
deployment — see [limitations](limitations.md).

## 2. A researcher studying tool-using agents

**The question:** "Does my method improve tool selection under permission constraints?"

**Why AOBench:** it is the only benchmark on [the comparison table](comparison.md) that
scores tool use, grounding, and authorisation jointly on the same trace, so you can ask
whether an intervention that improves one degrades another. The `ToolUseScorer` is
BFCL-decomposed, so tool-use numbers are interpretable next to that literature.

**What to run:** the deterministic subset for exact reproducibility, with
`aobench robustness` at k=5 so your effect is not a sampling artifact, and
`aobench compare runs` against a baseline.

**Citing:** cite the version you ran, and report split, profile, and adapter — see
[reproducing results](reproducing-results.md).

## 3. A model developer wanting a harder evaluation

**The question:** "Chat benchmarks are saturated. What still separates our models?"

**Why AOBench:** the tool-free `direct_qa` baseline scores about **0.33** on the
canonical first task. Tool-using models beat it — but the governance and grounding
axes stay stubborn, because they penalise confident invention and role overreach
rather than rewarding fluency. Those are the axes where models still differ.

**What to run:** the full dev split across your model line, then `aobench clear` for a
single comparable number per model, then slice by QCAT to find where the line breaks.

## 4. A team gating CI on agent quality

**The question:** "Did our last prompt change make the agent worse?"

**What to run:** a pinned AOBench version, a fixed task subset, and a score threshold
in CI. See [CI integration](../guides/ci-integration.md).

**Why it works:** determinism. The same snapshot and the same deterministic tasks give
the same score, so a regression is a real regression rather than sampling noise —
provided you avoid the rubric-scored tasks in the gate.

## 5. Teaching HPC operations

**The question:** "How do I show students what cluster operations actually involves?"

AOBench's 29 environments are readable case studies: a real Marconi100 GPU running
away thermally, a rack cooling fault, a node-down incident, an OOM job failure. The
[environment catalog](../reference/environment-catalog.md) is a set of scenarios with
the evidence attached, and the [task catalog](../reference/task-catalog.md) is a set of
questions a competent operator should be able to answer from them. Students can attempt
the tasks themselves before seeing what a model does.

## Not a use case

- **Certifying an agent as safe for production.** AOBench cannot do this. See
  [limitations](limitations.md).
- **Ranking general-purpose models.** Use a general benchmark; AOBench measures one
  narrow domain.
- **Evaluating your cluster.** AOBench evaluates agents, not machines. For hardware
  throughput you want MLPerf or the HPC benchmarks you already run.

---

**Using AOBench for something not listed here?** Add yourself to
[adopters](https://github.com/MSKazemi/aobench/discussions) or tell us in
[discussions](https://github.com/MSKazemi/aobench/discussions) — knowing the real uses
is what shapes the roadmap.
