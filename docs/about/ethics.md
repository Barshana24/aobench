---
title: "Responsible use of AOBench — ethics of benchmarking operational agents"
description: "Why AOBench treats authorisation as unrecoverable, what a benchmark score does and does not license, responsible disclosure for agent failures, and the risks of evaluating agents that operate real infrastructure."
keywords:
  - AI agent safety
  - responsible evaluation
  - infrastructure agent risk
  - benchmark ethics
---

# Responsible use

AOBench evaluates agents that people are considering pointing at real supercomputers.
That makes some of the usual benchmark conventions inadequate, and it makes a few
obligations run in both directions.

## The position this benchmark takes

**Authorisation is not a soft metric.**

Most benchmarks treat constraint violations as a deduction. AOBench zeroes the task.
An agent that produces a perfect diagnosis by reading data its role may not read has
not done the job well with a caveat — it has done something that, in a real facility,
would be an incident. Scoring it as 0.9-with-a-note would encode the wrong idea about
what operational competence means.

This is an opinion, and reasonable people disagree with it. It is stated here rather
than buried in a scorer so that anyone comparing AOBench numbers understands what they
are comparing.

## What a score licenses

**A high AOBench score licenses further evaluation. It does not license deployment.**

AOBench runs against frozen snapshots and mock tools. It cannot observe what happens
when an action has a consequence, when state changes underneath the agent, when a tool
is slow or wrong, or when two operators act at once. Every one of those is where real
operational failure comes from.

Concretely, the following claim is **not supported** by any AOBench result, and we ask
that it not be made:

> "Our agent scores X on AOBench, so it is safe to run on production HPC systems."

The supportable claim is narrower and still useful:

> "Our agent scores X on AOBench v0.4.1 (dev split, `default_hpc_v01`), with N RBAC
> hard-fails across 67 tasks."

## For people evaluating a vendor's agent

- **Look at the hard-fail count before the aggregate score.** An agent that scores well
  overall while occasionally overstepping its role is the more dangerous profile,
  because it will look reliable until it is not.
- **Run `aobench robustness` with k ≥ 5.** A single-shot score hides inconsistency, and
  inconsistency is the operational failure mode that matters.
- **Check grounding, not just outcome.** An agent that gets the right answer without
  supporting evidence got lucky, and luck does not generalise to your cluster.

## For people evaluating their own agent

If AOBench surfaces a class of failure in your system, that is the benchmark working.
Publishing your own weak numbers alongside what you did about them is more useful to
the field than another table of wins, and it is welcome in
[discussions](https://github.com/MSKazemi/aobench/discussions).

## Responsible disclosure of agent failures

AOBench can be used to find prompts on which a specific commercial agent oversteps its
permissions. That is legitimate and valuable safety research. We ask that you:

1. **Tell the vendor first**, with the task IDs and the trace, and give them reasonable
   time to respond.
2. **Publish the method and the aggregate finding** rather than a ready-to-use exploit
   against a named deployed system.
3. **Do not test against systems you are not authorised to test**, including any real
   facility. AOBench needs no such access, which is part of the point.

Security issues in AOBench itself go through
[SECURITY.md](security.md), not the public issue tracker.

## Data ethics

The corpus contains no personal data. Synthetic bundles use invented users and jobs;
grounded bundles derive from CINECA's already-public, anonymised ExaData release, where
identifiers refer to hardware and workloads rather than to people. The full provenance
record is in the [datasheet](datasheet.md).

If you contribute an environment built from your own facility's data, **sanitisation is
your responsibility and we will review it as if it were not** — see
[adding an environment](../framework/environments.md). Usernames, project names,
job scripts, and paths routinely leak identity in HPC data.

## Dual-use

An evaluation of how well agents operate infrastructure is also, read differently, a
map of where such agents fail. We judge the balance clearly favourable: the failures
are ones operators need to know about before deployment, not novel attack techniques,
and the environments are snapshots of a decommissioned public research machine. If you
disagree, [say so](https://github.com/MSKazemi/aobench/discussions) — that is a
conversation worth having in the open.

## Environmental note

Benchmarking large models costs energy, which is a slightly awkward thing to say about
a benchmark whose subject matter includes energy efficiency. Two practical mitigations:
the [Lite subset](../reference/glossary.md#benchmark-structure) exists so you do not
have to run everything to learn something, and the `direct_qa` baseline plus the
deterministic scoring path cost nothing at all. Please do not re-run the full suite in
CI on every commit — pin a subset.
