---
title: "AOBench FAQ — questions about benchmarking AI agents on HPC systems"
description: "Answers to the questions people actually ask about AOBench: what it measures, whether you need a cluster, how it differs from SWE-bench and tau-bench, how scores are computed, how to cite it, and when not to use it."
keywords:
  - AOBench FAQ
  - HPC agent benchmark questions
  - how to evaluate an LLM agent
---

# Frequently asked questions

## About the project

### What is AOBench?

AOBench (Agent Operations Benchmark) is an open-source Python benchmark framework for
evaluating AI agents that operate High-Performance Computing systems. It scores agents
on HPC operational tasks — job scheduling, telemetry interpretation, energy reasoning,
policy enforcement — against deterministic environment snapshots with mock HPC tools.

### What does "agent operations" mean?

The work a human operator does on a cluster: diagnosing why a job failed, deciding
whether a node is degraded, checking whether a request is within someone's permissions,
attributing a power anomaly to a rack. It is not code generation and it is not
general assistance. It is running a machine.

### Who is AOBench for?

HPC centres evaluating whether to let an agent near their operations; researchers
working on tool-using or ops agents who need a domain-specific, permission-aware
benchmark; and model developers who want a harder-than-chat evaluation with a
governance axis. See [use cases](use-cases.md).

### Is it production-ready?

No, and the version number says so. AOBench is v0.x: the task corpus, the schemas, and
the scoring profiles still change between minor versions. It is stable enough to
publish results from — provided you report the version, the split, and the profile —
and that is exactly what [reproducing results](reproducing-results.md) explains how to
do. See [limitations](limitations.md) for the honest list.

### Who maintains it?

Mohsen Seyedkazemi Ardebili and Andrea Bartolini, at the Department of Electrical,
Electronic and Information Engineering (DEI), University of Bologna. See
[GOVERNANCE.md](https://github.com/MSKazemi/aobench/blob/main/GOVERNANCE.md) for how
decisions get made and how you become a maintainer.

## Running it

### Do I need an HPC cluster?

No. Every task runs against a frozen snapshot bundle and mock tools. A laptop is
enough, and nothing you do can touch a real machine — that is a design property, not
a limitation of the current release.

### Do I need an API key?

Not for the first run. The `direct_qa` adapter is a tool-free baseline that runs
offline. You need a key only when you evaluate a hosted model through the `openai` or
`anthropic` adapters, and you pay that provider's usual costs.

### How long does a full run take?

The 67-task dev split against a hosted model is dominated by provider latency, not by
AOBench: expect tens of minutes and a few dollars for a mid-size model. The `direct_qa`
baseline over the same split finishes in under a minute.

### Which models and agents can I evaluate?

Anything reachable through one of the four adapters: `direct_qa` (baseline), `openai`
(any OpenAI-compatible endpoint, including local servers), `anthropic`, and `mcp` (any
MCP server, which is the general escape hatch). To evaluate a bespoke agent, write a
~40-line adapter — see [evaluate your own agent](../guides/evaluating-your-own-agent.md).

### Can I run it in CI?

Yes, and that is a supported use: pin a version, run a subset, and fail the build if
the score regresses. See [CI integration](../guides/ci-integration.md).

### Why is the `test` split locked?

Because a held-out split that anyone can read is not held out. The 21 test tasks
require `AOBENCH_UNLOCK_TEST=1`, which makes accidental training-on-test an explicit
act rather than an oversight. Use `--split dev` for everyday work.

## Scoring

### How is a run scored?

AOBench records the agent's full execution trace — every tool call, its arguments, its
result, and every message — and scores it across seven weighted dimensions: outcome
correctness, tool-use correctness, grounding, governance/RBAC, robustness, efficiency,
and workflow. See [scoring dimensions](../framework/scoring-dimensions.md).

### Why score the trace rather than the answer?

Because in operations, *how* you got the answer is part of whether the answer is
acceptable. An agent that guesses the right node ID without looking at telemetry has
not diagnosed anything, and an agent that reads a payroll file to answer a scheduling
question has done something disqualifying regardless of its answer.

### What is a hard fail?

An RBAC violation zeroes the entire task score, no matter how good the answer was.
There is no partial credit for a permission breach. This is the single most
opinionated thing about AOBench's scoring, and it is deliberate.

### What is the CLEAR scorecard?

An aggregation of a whole run into five comparable axes — **E**fficacy, **A**ssurance,
**R**eliability, **C**ost, **L**atency — so two models can be compared with one number
each. Produced by `aobench clear run`.

### What is pass^k?

The probability that an agent succeeds on *all* of k independent attempts, as opposed
to pass@k (succeeds on at least one). For operations, consistency matters more than
best-of-k: an agent that is right four times out of five is not a safe operator.
`aobench robustness task --n 5` measures it.

### Why did my score change between versions?

Because the corpus or the weights changed. That is why the
[versioning policy](versioning.md) asks you to report the AOBench version, the split,
the scoring profile, and the adapter alongside any number. Scores are comparable
*within* a version, not across them.

### Can I define my own scoring weights?

Yes — add a profile to `benchmark/configs/scoring_profiles.yaml` and pass it. Report
which profile you used; a custom profile makes your number incomparable to everyone
else's unless you say so.

## Comparisons

### How is this different from SWE-bench?

SWE-bench measures whether an agent can repair a software repository. AOBench measures
whether an agent can operate a supercomputer. Different domain, different tools,
different failure modes — and AOBench adds a permission axis that code benchmarks have
no equivalent for. Full table in [comparison](comparison.md).

### How is this different from tau-bench or BFCL?

Those measure tool and function calling in general. AOBench scores tool use *inside HPC
scenarios* and combines it with governance, grounding, robustness, and efficiency.
AOBench's `ToolUseScorer` is BFCL-decomposed, so the tool-use axis is deliberately
comparable in spirit.

### Is this a leaderboard?

There is [a leaderboard](../leaderboard.md), but it is not the point. The point is a
reproducible evaluation you can run yourself, on your own agent, without asking
anyone's permission.

## Data

### Where does the data come from?

Twenty-three environments are synthetic, built to cover specific operational
scenarios. Six are constructed from the public **Marconi100 ExaData** release —
real Slurm records and real telemetry from CINECA's 980-node Tier-0 supercomputer.
Eight of the 88 tasks target those grounded environments. Details in the
[datasheet](datasheet.md) and the [M100 guide](../guides/m100_environments.md).

### Is any of it personal or sensitive data?

No. The synthetic bundles contain invented users and jobs. The M100-grounded bundles
derive from a public, already-anonymised research dataset. See the
[datasheet](datasheet.md) for the full provenance record.

### Can I contribute a snapshot from my own cluster?

Yes, please — that is the single most valuable contribution to this project. A
sanitised bundle from a real facility is worth more than any amount of synthetic
data. Start a [discussion](https://github.com/MSKazemi/aobench/discussions) and read
[the environment format](../framework/environments.md).

## Contributing and citing

### How do I cite AOBench?

Cite the version you actually ran. BibTeX, the four fields to report with any score,
and when to also cite ExaData are in [how to cite](citation.md); the machine-readable
forms are `CITATION.cff`, `CITATION.bib`, `codemeta.json`, and `.zenodo.json`.

### How do I contribute?

Pick a [good first issue](https://github.com/MSKazemi/aobench/labels/good%20first%20issue) —
each one names the files to touch and an honest time estimate. Bug fixes, docs, tests,
examples, and new CLI flags need no prior discussion. See
[contributing](contributing.md).

### I found a mistake in the benchmark itself. A wrong gold answer?

Please open an issue with the task ID. Wrong gold answers are the most damaging bug a
benchmark can have, and reports of them are treated as high priority rather than as
criticism.

### What licence is it under?

Apache 2.0, for both the code and the corpus.
