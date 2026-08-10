---
title: "AOBench limitations — when not to use this benchmark"
description: "An honest account of what AOBench cannot measure: mock tools instead of live systems, corpus size, synthetic RBAC policies, judge variance, single-turn tasks, and what a high score does and does not license."
keywords:
  - benchmark limitations
  - when not to use AOBench
  - agent evaluation validity
---

# Limitations — and when not to use AOBench

A benchmark that only advertises its strengths is a marketing document. This page is
the one to read before you cite an AOBench number, and the one to quote back at anyone
who over-claims from one — including us.

## The load-bearing caveat

**A high AOBench score is not evidence that an agent is safe to run against production
infrastructure.**

AOBench measures behaviour against frozen snapshots and mock tools. It cannot observe
what happens when a tool is slow, when state changes mid-task, when two operators act
at once, or when an action has a consequence. Passing AOBench is necessary-ish and
nowhere near sufficient for operational deployment. Treat it as a screening
instrument: a low score is strong evidence against; a high score merely fails to rule
out.

## Structural limitations

### Mock tools, not live systems

Every tool reads from a snapshot directory. Nothing executes. This buys
reproducibility, publishability, and safety — and costs realism. Real systems return
errors, time out, contradict themselves, and change while you are looking at them.
None of that is in scope. [OSWorld](comparison.md#osworld) and
[SWE-bench](comparison.md#swe-bench) sit at the other end of this trade-off.

### Single-turn tasks, no simulated user

Each task is one query. There is no back-and-forth, no clarifying question, no user who
changes their mind. Real operational work is conversational, and agents that are good
at asking a clarifying question get no credit for it here.

### Corpus size limits statistical power

88 tasks total. Sliced by QCAT you are down to 5–16 tasks per category, and by role ×
QCAT to a handful. **Per-slice differences between two models are usually not
statistically meaningful** — report confidence intervals, and be sceptical of anyone
who ranks models on a five-task slice, including your own analysis.

### Synthetic RBAC policies everywhere

Every RBAC policy in the corpus is invented, including in the M100-grounded
environments — real site authorisation models were not available. The governance
dimension therefore measures adherence to *a plausible* permission model, not to any
real centre's. Sites with finer-grained or differently-shaped authorisation should
expect their own model to behave differently.

### Five roles is a simplification

Real facilities have dozens of overlapping groups, project allocations, and delegated
rights. Five roles is a tractable abstraction, not a faithful one.

### One operational culture

The corpus reflects European Tier-0 practice, largely CINECA's. Conventions about what
counts as a correct diagnosis, an acceptable escalation, or a reasonable answer are
not universal. A site with different norms may see correct-for-them behaviour scored
as wrong.

## Measurement limitations

### Rubric-scored tasks depend on a judge model

Deterministic tasks are exactly reproducible. Rubric tasks are scored by an LLM judge
and therefore carry judge variance and judge bias, including possible favouritism
toward outputs resembling the judge's own family. If you compare models, prefer the
deterministic subset or report both. See [reproducing results](reproducing-results.md).

### Gold answers are not multiply annotated

They were authored and reviewed by the maintainers, not independently re-annotated by
a panel of HPC operators. Some are certainly wrong. **Reports of wrong gold answers are
high-priority bugs, not criticism** —
[file them](https://github.com/MSKazemi/aobench/issues/new/choose).

### Grounding is scored against recorded evidence

The grounding dimension checks whether an answer is supported by evidence in the
bundle. An answer that is correct about the real world but unsupported by the snapshot
scores badly. That is the intended behaviour, and it is also a source of false
negatives.

### Contamination is possible and only partly mitigated

Task specs are public and on GitHub, so they may be in a model's training data. Tasks
carry a `contamination_risk` field and the test split is locked, but neither
eliminates the problem. Numbers from models trained after a corpus release should be
read with this in mind.

### Efficiency and cost are proxies

The efficiency dimension counts work done, not wall-clock resources on a real system.
CLEAR's cost axis uses provider pricing or a token proxy, which is not the same as the
cost of running an agent in a facility.

## Scope limitations

AOBench does **not** measure, and should not be cited about:

- General reasoning, mathematics, or knowledge.
- Code generation or software repair.
- Web browsing or computer use.
- Conversational quality or helpfulness.
- Real-time control, actuation, or anything with a physical consequence.
- Multi-agent coordination beyond the A2A conformance scorers.
- Security in the adversarial sense — the governance dimension checks role adherence,
  not resistance to prompt injection or to a determined attacker.

## Version stability

AOBench is v0.x. Task specs, schemas, and scoring profiles change between minor
versions, and they have changed in ways that move scores. **Numbers are comparable
within a version, not across versions**, unless the [versioning policy](versioning.md)
explicitly says otherwise for that pair of releases.

## What we are doing about it

Several of the above are tracked as open work rather than accepted permanently:

| Limitation | Tracking |
|---|---|
| Corpus size and slice power | Corpus expansion — contributions very welcome |
| Synthetic RBAC | Seeking a real, sanitised site policy to model against |
| No live execution | Containerised HPC terminal runner ([issue #19](https://github.com/MSKazemi/aobench/issues/19)) |
| Judge variance | Deterministic-path expansion and judge-agreement reporting |
| Single-turn only | Multi-turn task design under consideration |

If one of these blocks your use of AOBench, say so in
[discussions](https://github.com/MSKazemi/aobench/discussions) — knowing which
limitation actually bites is what decides the order they get fixed in.
