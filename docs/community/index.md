---
title: "The AOBench community — how to get involved"
description: "How the AOBench project is run, where conversations happen, what contributions are most needed, and what you can expect from the maintainers."
keywords:
  - open source community
  - contribute to AOBench
  - HPC agent research community
---

# Community

AOBench is a small project that would like to be a useful one. That depends on people
outside Bologna running it, disagreeing with it, and fixing it.

## Where things happen

| Space | For |
|---|---|
| [Discussions](https://github.com/MSKazemi/aobench/discussions) | Questions, ideas, results you got, "is this a bug or am I holding it wrong" |
| [Issues](https://github.com/MSKazemi/aobench/issues) | Bugs, concrete proposals, task and environment contributions |
| [Good first issues](https://github.com/MSKazemi/aobench/labels/good%20first%20issue) | Small, well-specified work with an honest time estimate |
| [Start here (#20)](https://github.com/MSKazemi/aobench/issues/20) | A map of every open area to a first task |
| [Security advisories](https://github.com/MSKazemi/aobench/security/advisories/new) | Vulnerabilities — please not the public tracker |

**Questions are welcome and expected.** If the docs did not answer something, that is a
documentation bug, and asking is how we find out.

## What we most need

Ordered by how much difference it makes, not by how hard it is:

1. **An environment snapshot from a real facility.** Twenty-three of twenty-nine
   environments are synthetic. One sanitised window from a cluster that is not
   Marconi100 would improve this benchmark more than months of our own work.
   See [adding an environment](../guides/adding-an-environment.md).
2. **Tasks.** Corpus breadth is what limits what AOBench can measure — especially
   `DATA` and `PERF`, which are thin because neither maintainer is a storage
   specialist. See [adding a task](../guides/adding-a-task.md).
3. **Results.** Run it on your agent and publish the numbers, including bad ones.
   See the [leaderboard](../leaderboard.md).
4. **Adapters.** Every new adapter makes a whole class of agent evaluable by everyone.
5. **Reports that we got something wrong.** Especially a wrong gold answer — those are
   the most damaging bug a benchmark can have, and reporting one is a favour, not a
   criticism.
6. **Code, docs, tests.** The usual, always welcome.

## What you can expect from us

- **A first response within 3 working days**, even if it is only "seen, I'll look
  properly on Friday".
- **If a PR goes quiet for over a week, ping it.** That is our failure, not rudeness on
  your part.
- **Credit.** Every merged contribution earns a line in
  [AUTHORS.md](https://github.com/MSKazemi/aobench/blob/main/AUTHORS.md) and a mention
  in the release notes. Substantial corpus or methodological work may warrant paper
  co-authorship — if you think that applies to you, say so.
- **Public reasoning.** Decisions are made in issues, with the argument written down.
  See [GOVERNANCE.md](https://github.com/MSKazemi/aobench/blob/main/GOVERNANCE.md).

## What helps us

- **PRs under ~300 changed lines.** Bug fixes, docs, tests, examples, and new CLI flags
  need no prior discussion — just send them.
- **Open an issue first** only if you are changing the task schema, the scoring weights,
  the RBAC model, or a public CLI signature.
- **You do not need HPC access.** The whole benchmark runs against frozen snapshots on
  a laptop, and `direct_qa` needs no API key.

## For researchers

[RESEARCH.md](https://github.com/MSKazemi/aobench/blob/main/RESEARCH.md) lists sixteen
open questions AOBench can now answer empirically. Several are good MSc or PhD
projects; a couple are a good afternoon. We are happy for you to publish first-author,
and co-supervision is possible for students at any institution.

**Negative results are welcome here.** "We tried X and it did not help" is a real
contribution to a young field, and this project will link it rather than bury it.

## Code of conduct

The [Code of Conduct](https://github.com/MSKazemi/aobench/blob/main/CODE_OF_CONDUCT.md)
applies everywhere. Short version: disagree about the benchmark as much as you like,
and be decent to the person you are disagreeing with.
