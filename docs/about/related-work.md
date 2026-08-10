---
title: "Related work — agent benchmarks, HPC operations, and AIOps research"
description: "The research AOBench builds on: agent benchmarks, tool-use evaluation, LLM-as-judge methodology, HPC operational data and AIOps, and where AOBench sits among them."
keywords:
  - agent benchmark related work
  - AIOps research
  - LLM as judge
  - HPC operational data
---

# Related work

Where AOBench sits in the literature, and which ideas it borrowed from where. This is
a positioning page, not an exhaustive survey; the citation keys match
[`docs/references.bib`](https://github.com/MSKazemi/aobench/blob/main/docs/references.bib).

## Agent benchmarks

The evaluation of LLM agents matured rapidly from single-answer QA into
environment-grounded, trace-aware assessment.

**SWE-bench** [@jimenez2024swebench] established that a benchmark can use a real
artifact (a repository) and a real oracle (a hidden test suite), and that agents can be
scored on whether the world ends up in the right state rather than on what they said.
AOBench takes the end-state framing and applies it to a facility, but has no equivalent
of the hidden test suite — an operational diagnosis has no `pytest`.

**AgentBench** [@liu2024agentbench] showed that agentic ability is not one capability:
models rank differently across its eight environments. That result is the direct
argument for domain-specific benchmarks such as this one.

**GAIA** [@mialon2023gaia] demonstrated how far a well-designed general assistant
benchmark can separate models with conceptually simple questions. Its exact-match final
answer is the opposite of AOBench's trace scoring — a deliberate contrast.

**τ-bench** [@yao2024taubench] is the closest relative: policy adherence, a simulated
user, database end-state scoring, and the **pass^k** consistency metric that AOBench
adopts. AOBench's departures are a machine-checkable RBAC policy instead of a
natural-language one, a hard fail instead of a deduction, and no simulated user.

**OSWorld** [@xie2024osworld] runs agents against real operating systems in VMs with
execution-based verification, which is more realistic than any snapshot approach and
correspondingly harder to reproduce or publish. AOBench sits at the other end of that
trade-off on purpose.

**MLAgentBench** [@huang2024mlagentbench] evaluates agents doing ML research
engineering — closest to AOBench in the "agent operating on research infrastructure"
sense, without a permission model.

## Tool use and function calling

**BFCL** (Berkeley Function Calling Leaderboard) [@patil2024bfcl] is the reference for
decomposed function-calling evaluation: function selection, argument correctness,
types, and execution. AOBench's `ToolUseScorer` follows the same decomposition
deliberately, so a tool-use number here is interpretable next to a BFCL number.

**Gorilla** [@patil2023gorilla] and **ToolLLM** [@qin2024toolllm] established that
tool-use ability is trainable and measurable independently of general ability — which
is why AOBench separates the tool-use dimension from the outcome dimension rather than
collapsing them.

**ToolEmu** [@ruan2024toolemu] uses an LLM to emulate tool execution in order to probe
agent risk without real consequences. AOBench's mock tools serve the same safety
purpose with frozen data instead of an emulator, trading generality for determinism.

## Evaluation methodology

**LLM-as-a-judge** [@zheng2023judging] documented both the practicality of model-based
scoring and its failure modes — position bias, verbosity bias, self-preference. Those
findings are why AOBench keeps a deterministic scoring path as the primary one and
treats the rubric path as a documented source of variance
([limitations](limitations.md)).

**Datasheets for Datasets** [@gebru2021datasheets] and **Model Cards**
[@mitchell2019modelcards] provide the documentation structure AOBench follows in its
[datasheet](datasheet.md) and [benchmark card](benchmark-card.md).

**pass@k and its discontents** [@chen2021codex] introduced pass@k for code generation.
τ-bench's pass^k inversion — all k must succeed — is the right adaptation for
operations, where an inconsistent operator is an unsafe one.

**TRAIL** [@trail2025taxonomy] provides the error taxonomy AOBench adapts to 24 HPC
leaves, so a failing run can be described by *how* it failed rather than only that it
did.

## HPC operations, telemetry, and AIOps

**ExaData / Marconi100** [@borghesi2023m100; @exadata2023] is the public release of
operational data — Slurm records, node telemetry, facility measurements — from
CINECA's 980-node Tier-0 supercomputer. It is the source of AOBench's six grounded
environments and the reason the benchmark can claim any real-world fidelity at all.
*Disclosure: both AOBench maintainers are among the authors of that dataset paper.*

**Anomaly detection on HPC telemetry** [@borghesi2019anomaly; @molan2024graafe] is the
line of work that establishes which signals matter operationally — thermal, power,
node-health — and therefore which scenarios are worth building tasks around.

**AIOps surveys** [@notaro2021aiops] map the operational tasks that automation has
historically targeted: anomaly detection, root-cause analysis, incident triage. Those
categories map closely onto AOBench's `AIOPS`, `MON`, and `PERF` QCATs.

**Agents for HPC operations** is an emerging area with, so far, more position papers
than evaluations. That gap is the reason AOBench exists.

## What AOBench contributes

Reading the above together, the specific gap AOBench fills:

1. **A machine-checkable authorisation dimension with a hard fail.** No agent benchmark
   in this list treats role compliance as unrecoverable.
2. **HPC-native tools and scenarios** rather than generic OS or API surfaces.
3. **Real Tier-0 operational data** in a reproducible, publishable snapshot format.
4. **Joint scoring** of outcome, tool use, grounding, governance, robustness,
   efficiency, and workflow on one trace, so trade-offs between them are visible.

## Contributing to this page

If your work belongs here — especially work on agents for infrastructure operations, or
another HPC operational dataset — please
[open a PR or a discussion](https://github.com/MSKazemi/aobench/discussions). Being
described accurately is a reasonable thing to want, and a positioning page written only
by us is a positioning page with blind spots.
