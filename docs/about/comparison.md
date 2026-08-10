---
title: "AOBench vs SWE-bench, tau-bench, BFCL, AgentBench, GAIA — an honest comparison"
description: "How AOBench compares to the major AI agent benchmarks: what each one measures, where AOBench is genuinely different, and which benchmark you should actually use for your question."
keywords:
  - AOBench vs SWE-bench
  - agent benchmark comparison
  - tau-bench alternative
  - best benchmark for tool-using agents
  - open-source agent evaluation
---

# AOBench compared with other agent benchmarks

**Short answer: if your question is "can this agent operate a computing system
correctly, safely, and within its role?", use AOBench. For almost any other question,
one of the benchmarks below is a better fit, and this page will tell you which.**

A comparison page that concludes "ours is best at everything" is worthless to a
reader and, frankly, to us. AOBench is narrow on purpose. Below is where it wins,
where it loses, and where it is simply measuring something else.

## At a glance

| Benchmark | Domain | Environment | Scored on | Permission axis |
|---|---|---|---|---|
| **AOBench** | HPC operations | Frozen snapshots + mock tools | Full trace, 7 dimensions | **Yes — hard fail** |
| SWE-bench | Software repair | Real repos + test suites | Patch passes tests | No |
| τ-bench (tau-bench) | Retail/airline customer service | Simulated API + user LLM | Final DB state, pass^k | Policy adherence, not RBAC |
| BFCL | Function calling | Stateless function schemas | Call correctness (AST/exec) | No |
| AgentBench | Broad agent ability | 8 heterogeneous environments | Per-environment success | No |
| GAIA | General assistant reasoning | Web + files | Final answer exact match | No |
| MLAgentBench | ML research engineering | Real ML codebases | Task-specific improvement | No |
| OSWorld | Desktop GUI operation | Real OS in a VM | End-state verification | No |
| MLPerf | System throughput | Real hardware | Time / throughput | N/A (not an agent benchmark) |

## Benchmark by benchmark

### SWE-bench

**Measures:** whether an agent can resolve a real GitHub issue such that the
repository's hidden tests pass.

**Compared to AOBench:** different domain entirely. SWE-bench's environment is a
codebase; AOBench's is a machine. SWE-bench's oracle is a test suite, which is a much
cleaner success signal than anything AOBench has — that is a genuine advantage of
theirs. AOBench's advantage is that operational correctness is not binary: an answer
can be right and still unacceptable because of how it was obtained.

**Use SWE-bench if:** you are evaluating a coding agent. **Use AOBench if:** you are
evaluating an agent that will be given a cluster.

### τ-bench (tau-bench)

**Measures:** whether an agent can complete customer-service tasks against a simulated
user and a database, following a written policy, consistently across trials.

**Compared to AOBench:** the closest philosophical relative. τ-bench also cares about
policy adherence and about consistency (it popularised the pass^k framing that AOBench
adopts). The differences: AOBench's policy axis is machine-checkable RBAC rather than
natural-language policy, it hard-fails rather than deducts, and the domain is
infrastructure operations rather than retail. τ-bench's simulated user is something
AOBench does not have and would benefit from.

**Use τ-bench if:** you want conversational policy-following. **Use AOBench if:** you
want role-enforced infrastructure operations.

### Berkeley Function Calling Leaderboard (BFCL)

**Measures:** whether a model emits the correct function call — right function, right
arguments, right types — across a large schema corpus.

**Compared to AOBench:** BFCL is a component benchmark; AOBench is a system benchmark.
AOBench's `ToolUseScorer` is deliberately BFCL-decomposed, so if a model does well on
BFCL and badly on AOBench's tool-use dimension, the gap is about HPC context rather
than about function-calling mechanics. BFCL is much larger, much cleaner, and much
better for isolating a model's calling ability.

**Use BFCL if:** you are improving a model's function-calling. **Use AOBench if:** you
want to know whether correct calls add up to a correct operation.

### AgentBench

**Measures:** LLM-as-agent ability across eight environments (OS, database,
knowledge graph, card game, and others).

**Compared to AOBench:** AgentBench is broad where AOBench is deep. Its OS environment
is the nearest overlap, but it tests shell competence rather than facility operations,
and it has no role or permission model. If you want one number for "is this model
agentic at all", AgentBench is the better instrument.

### GAIA

**Measures:** general assistant questions requiring reasoning, web browsing, and file
handling, with an exact-match final answer.

**Compared to AOBench:** GAIA scores the destination; AOBench scores the journey. GAIA
tasks are deliberately un-domain-specific. There is essentially no overlap — a model
can be excellent at one and useless at the other.

### MLAgentBench

**Measures:** whether an agent can improve an ML pipeline's metric by editing real
research code.

**Compared to AOBench:** shares the "agent operating on real research infrastructure"
spirit, but the object is a training script rather than a running facility. No
permission model, and success is a metric delta rather than a trace judgement.

### OSWorld

**Measures:** whether an agent can complete real desktop tasks in a real OS through a
GUI, verified by end-state execution scripts.

**Compared to AOBench:** OSWorld's environments are genuinely live, which is a
substantial realism advantage AOBench does not claim to match. AOBench trades that
realism for reproducibility: a frozen snapshot still produces the same score in five
years, and can be published without exposing a facility. Different point on the same
trade-off curve.

### MLPerf

**Measures:** system and hardware throughput on standard ML workloads.

**Compared to AOBench:** not an agent benchmark at all, listed because HPC people ask.
MLPerf tells you how fast your machine is. AOBench tells you whether an agent should be
allowed to touch it.

## What AOBench does that the others do not

1. **A machine-checkable permission axis with a hard fail.** Every task carries a role
   and an RBAC policy from the environment snapshot. Overstepping zeroes the score.
   No other benchmark on this page enforces authorisation as a first-class dimension.
2. **HPC-native tools.** SLURM, telemetry time series, facility/cooling data, site
   documentation, and RBAC policy — the actual instruments of the job.
3. **Grounding against a frozen snapshot.** Answers must be supported by evidence in
   the bundle, so confident invention is scored as the failure it is.
4. **Six environments built from real Tier-0 supercomputer data.** The Marconi100
   ExaData bundles replay real telemetry and Slurm records from a 980-node CINECA
   machine, so the scenarios are ones that actually happened.
5. **Reproducibility without infrastructure.** No cluster, no credentials, no cloud
   spend. A result from 2026 is re-derivable in 2031.

## What AOBench does worse

Stated plainly, because you will find out anyway:

- **Smaller.** 88 tasks against SWE-bench's thousands. Statistical power on any single
  slice is limited, and per-QCAT numbers should be read with that in mind.
- **Mock tools, not live systems.** OSWorld and SWE-bench execute for real. AOBench's
  fidelity is only as good as its snapshots, and mock tools cannot surprise an agent
  the way a real system can.
- **No simulated user.** τ-bench's user LLM produces multi-turn ambiguity that AOBench
  tasks, being single-shot queries, do not.
- **Rubric-scored tasks depend on a judge model.** Deterministic tasks do not, but for
  the rubric path the judge is a source of variance — quantified in the
  [reproducibility notes](reproducing-results.md).
- **Young.** v0.x, with schemas still moving. Cross-version comparisons need care.

## Choosing

| Your question | Use |
|---|---|
| Can this agent fix a bug in my repo? | SWE-bench |
| Can this model call functions correctly? | BFCL |
| Can this agent follow a policy over a conversation? | τ-bench |
| Is this model agentic at all, broadly? | AgentBench |
| Can this assistant answer hard general questions? | GAIA |
| Can this agent do ML research engineering? | MLAgentBench |
| Can this agent drive a desktop? | OSWorld |
| **Can this agent operate my cluster, safely, in role?** | **AOBench** |

Complementary, not competing. Several of the benchmarks above measure a capability
AOBench assumes. A sensible evaluation stack uses more than one.

---

*Found an error in how we described your benchmark? That is a bug and we want the
report — [open an issue](https://github.com/MSKazemi/aobench/issues/new/choose) and
we will fix it.*
