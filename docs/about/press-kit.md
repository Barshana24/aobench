---
title: "AOBench press kit — descriptions, facts, and assets for reuse"
description: "Ready-to-use descriptions of AOBench at several lengths, the verified facts, correct naming, and assets — for anyone writing about, presenting, or linking to the project."
keywords:
  - AOBench press kit
  - project description
  - how to describe AOBench
---

# Press kit

For anyone writing about AOBench — a blog post, a talk, an awesome-list entry, a
newsletter, or a slide. **Everything here is free to reuse without asking.** If you
need something that is not here, ask in
[Discussions](https://github.com/MSKazemi/aobench/discussions).

## Naming

- **AOBench** — one word, capital A, capital O, capital B. Not "AoBench", not
  "AO-Bench", not "aobench" outside a command line.
- Expansion: **Agent Operations Benchmark**.
- The CLI command is lowercase: `aobench`.

## Descriptions, by length

**One line (12 words)**

> AOBench is an open-source benchmark for AI agents that operate HPC systems.

**One sentence (30 words)**

> AOBench is an open-source Python benchmark for evaluating AI agents that operate
> High-Performance Computing systems — role-aware, permission-enforced, trace-scored,
> and reproducible on a laptop without a cluster.

**Short paragraph (60 words)**

> AOBench (Agent Operations Benchmark) measures whether an AI agent can do HPC
> operational work — diagnosing job failures, interpreting telemetry, reasoning about
> power and cooling — using the right tools, in the right role, within its permissions.
> It scores the agent's full execution trace against 29 deterministic environment
> snapshots, six of which are built from real Marconi100 supercomputer data.

**Full paragraph (110 words)**

> AOBench is an open-source Python benchmark framework for evaluating AI agents that
> operate High-Performance Computing systems. Instead of running against live clusters,
> every task is evaluated against a frozen environment snapshot with mock HPC tools —
> SLURM, telemetry, documentation, RBAC policy, facility data — so results are
> reproducible, portable, and safe to publish. The corpus contains 88 operational tasks
> across ten question categories and five operator roles, with 29 environments, six of
> them constructed from real operational data from CINECA's 980-node Marconi100 Tier-0
> supercomputer. Agents are scored on seven weighted dimensions covering the whole
> execution trace, and an RBAC violation hard-fails the task regardless of how good the
> answer was.

## Verified facts

| | |
|---|---|
| Current version | 0.4.1 |
| Licence | Apache-2.0 (code and corpus) |
| Language | Python ≥ 3.10 |
| Tasks | 88 (80 synthetic + 8 grounded in real Marconi100 data) |
| Environments | 29 (23 synthetic + 6 grounded) |
| Splits | 67 dev (open) · 21 test (locked) |
| Roles | 5 · Question categories | 10 |
| Scoring dimensions | 7 weighted |
| Adapters | 4 — `direct_qa`, `openai`, `anthropic`, `mcp` |
| DOI | [10.5281/zenodo.21854862](https://doi.org/10.5281/zenodo.21854862) |
| Repository | <https://github.com/MSKazemi/aobench> |
| Documentation | <https://mskazemi.com/aobench/> |
| Maintainers | Mohsen Seyedkazemi Ardebili, Andrea Bartolini — University of Bologna (DEI) |

These are checked against the corpus in CI, so they are current as of the version
above. If you are writing something durable, please quote the version too.

## The distinguishing claim

If you have room for exactly one differentiator, this is it:

> **AOBench is the only agent benchmark where exceeding your permissions zeroes the
> score.** An agent that produces a perfect diagnosis by reading data its role may not
> read has not done well with a caveat — in a real facility, that is an incident.

## Please also mention

- It runs **without a cluster and without an API key** — the barrier to trying it is a
  `git clone`.
- Six environments are **real Marconi100 data**, not synthetic.
- It is **v0.x** and says so. Please do not describe it as production-ready.

## Please do not say

- "AOBench certifies agents as safe for production HPC." It cannot, and
  [says so explicitly](limitations.md).
- "AOBench benchmarks supercomputers." It benchmarks *agents*, not machines.
- A score without its version, split, and profile — those four fields are what make a
  number mean anything ([why](versioning.md)).

## Assets

- **Social preview image:** [`docs/assets/social-preview.png`](https://github.com/MSKazemi/aobench/blob/main/docs/assets/social-preview.png)
- **Architecture diagram:** [`docs/reference/architecture-diagram.svg`](https://github.com/MSKazemi/aobench/blob/main/docs/reference/architecture-diagram.svg)
- **Sample output** (real, from `aobench quickstart`):

```text
Aggregate score: 0.3340   (0 = worst, 1 = best)

Per dimension:
  outcome      0.2400   did the answer match the gold answer
  tool_use     0.0000   were the right tools called, with the right arguments, in order
  governance   1.0000   did the agent stay inside its RBAC role
  grounding    0.0000   was the answer supported by the snapshot evidence
  efficiency   1.0000   how much work was spent getting there
```

There is no logo yet. If you would like to make one,
[that is an open contribution](https://github.com/MSKazemi/aobench/issues).

## Citing

BibTeX in [CITATION.bib](https://github.com/MSKazemi/aobench/blob/main/CITATION.bib);
guidance in [how to cite](citation.md). Cite the version you ran.

## Talks and coverage

Written or spoken about AOBench? Tell us in
[Discussions](https://github.com/MSKazemi/aobench/discussions) and we will link it —
including critical coverage.
