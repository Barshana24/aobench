---
title: "AOBench benchmark card — intended use, scope, and misuse boundaries"
description: "Model-card-style summary of AOBench: what it measures, intended and out-of-scope uses, evaluation protocol, known biases, ethical considerations, and what a score does and does not license."
keywords:
  - benchmark card
  - model card
  - intended use
  - responsible evaluation
---

# Benchmark card — AOBench v0.4.1

In the spirit of **Mitchell et al., "Model Cards for Model Reporting"** (FAT* 2019),
applied to a benchmark rather than a model. Companion documents: the
[datasheet](datasheet.md) (provenance) and [limitations](limitations.md) (validity).

---

## Basic information

| | |
|---|---|
| **Name** | AOBench (Agent Operations Benchmark) |
| **Version** | 0.4.1 |
| **Type** | Agent evaluation benchmark + framework |
| **Domain** | High-Performance Computing operations |
| **Licence** | Apache-2.0 (code and corpus) |
| **DOI** | [10.5281/zenodo.21854862](https://doi.org/10.5281/zenodo.21854862) |
| **Maintainers** | Seyedkazemi Ardebili, Bartolini — University of Bologna (DEI) |
| **Repository** | <https://github.com/MSKazemi/aobench> |

## What it measures

Whether an AI agent can perform HPC operational work — diagnosing job failures,
interpreting telemetry, reasoning about power and cooling, answering architecture and
policy questions — **using the right tools, in the right order, grounded in the
available evidence, and without exceeding the permissions of the role it is acting
as**.

Seven weighted dimensions, scored over the agent's full execution trace:

| Dimension | `default_hpc_v01` weight | Question it answers |
|---|---:|---|
| Outcome | 0.30 | Was the answer right? |
| Governance / RBAC | 0.20 | Did it stay inside its role? |
| Tool use | 0.15 | Right tools, right arguments, right order? |
| Grounding | 0.10 | Is the answer supported by the snapshot? |
| Robustness | 0.10 | Is it right *consistently* (pass^k)? |
| Workflow | 0.10 | Did the executed DAG match the gold workflow? |
| Efficiency | 0.05 | How much work did it take? |

An RBAC violation is a **hard fail**: the task scores zero regardless of the rest.

## Evaluation protocol

- **Environment:** deterministic frozen snapshot bundles with mock HPC tools. No live
  system is contacted; nothing executes.
- **Corpus:** 88 tasks across 10 QCATs × 5 roles; 29 environments, 6 of them built from
  real Marconi100 ExaData.
- **Splits:** 67 dev (open), 21 test (locked behind `AOBENCH_UNLOCK_TEST=1`).
- **Scoring paths:** deterministic (exact / numeric / set matching, with cascading
  failure propagation) and rubric (LLM judge). Deterministic tasks are exactly
  reproducible.
- **Aggregation:** `aobench clear run` reduces a run to Efficacy, Assurance,
  Reliability, Cost, Latency.

## Intended uses

1. **Screening** agents proposed for HPC operational assistance, before any exposure to
   real infrastructure.
2. **Research** on tool-using, permission-aware, or ops-domain agents.
3. **Regression testing** an agent in CI against a pinned version and subset.
4. **Comparing models** on a domain-specific axis that chat benchmarks do not cover.
5. **Teaching** HPC operations, using the environments as case studies.

## Out-of-scope uses

**Do not use an AOBench score to:**

- **Certify or advertise an agent as safe for production infrastructure.** AOBench
  cannot observe consequences, concurrency, latency, or state change. This is the most
  important line on this page.
- **Make claims about general reasoning, coding, or assistant ability.** Different
  benchmarks measure those; see [comparison](comparison.md).
- **Compare numbers across AOBench versions** without checking the
  [versioning policy](versioning.md).
- **Rank models on a single QCAT or role slice.** Slices contain 5–16 tasks; the
  differences are usually not meaningful.
- **Substitute for a security review.** The governance dimension checks role adherence
  against a policy, not resistance to prompt injection or to an adversary.

## Factors and known biases

**Operational culture.** The corpus reflects European Tier-0 practice, largely
CINECA's. Correct-for-your-site behaviour may score as wrong.

**Synthetic authorisation.** Every RBAC policy in the corpus is invented, including in
the grounded environments. The governance dimension measures adherence to a plausible
model, not to a real one.

**Role granularity.** Five roles is a coarse abstraction of real facility
authorisation.

**Judge dependence.** Rubric-path tasks inherit the judge model's biases, potentially
including favouritism toward outputs from its own model family.

**Contamination.** Task specs are public. Models trained after a corpus release may
have seen them; the `contamination_risk` field and the locked test split mitigate but
do not eliminate this.

**Language.** English only.

## Metrics and their caveats

- **Aggregate score** is profile-dependent and meaningless without naming the profile.
- **Governance** is engagement-aware, so an agent that refuses everything cannot farm
  it — but it still rewards caution, which is intentional and worth stating when you
  report it.
- **Efficiency** counts work, not real resource cost.
- **Cost** in CLEAR uses provider pricing or a token proxy, not facility cost.
- **pass^k** at small k has wide confidence intervals; report k and the interval.

## Ethical considerations

Agents that operate computing infrastructure can cause real harm — wasted allocation,
disrupted science, damaged hardware, exposed data. AOBench's design position is that
**authorisation is not a soft metric**, which is why a permission violation is
unrecoverable rather than a deduction. Fuller discussion in [ethics](ethics.md).

The benchmark is also usable to find the prompts on which an agent *does* overstep. We
consider that legitimate and valuable safety research, and ask that findings about a
specific vendor's agent go to that vendor before they go public.

## Reporting an AOBench result

State all four, always:

1. AOBench **version** (e.g. `0.4.1`)
2. **Split** (`dev` or `test`)
3. **Scoring profile** (e.g. `default_hpc_v01`)
4. **Adapter and model** (e.g. `openai:gpt-4o`)

Plus, if you used the rubric path, the judge model. See
[reproducing results](reproducing-results.md) and [how to cite](citation.md).

## Maintenance and feedback

Actively maintained; see [ROADMAP](https://github.com/MSKazemi/aobench/blob/main/ROADMAP.md) and
[GOVERNANCE.md](https://github.com/MSKazemi/aobench/blob/main/GOVERNANCE.md).
Corrections to the corpus — especially **wrong gold answers** — are high-priority bugs.
[File one](https://github.com/MSKazemi/aobench/issues/new/choose).
