# Authors and contributors

AOBench is built by the people below. **Every merged contribution earns a line here,
whatever its size** — a typo fix in the docs is a real contribution to a project whose
docs are the product.

## Maintainers

- **Mohsen Seyedkazemi Ardebili** ([@MSKazemi](https://github.com/MSKazemi)) —
  ORCID [0000-0002-1166-6559](https://orcid.org/0000-0002-1166-6559) —
  University of Bologna (DEI)
- **Andrea Bartolini** —
  ORCID [0000-0002-1148-2450](https://orcid.org/0000-0002-1148-2450) —
  University of Bologna (DEI)

## Contributors

Added when a first PR merges, newest last.

- **abhinav** ([@erensh27](https://github.com/erensh27)) — AOBench's first external
  contributor. Took [issue #2](https://github.com/MSKazemi/aobench/issues/2) and replaced
  the raw traceback on a mistyped `--task` / `--env` with an actionable one-line error,
  with end-to-end CLI tests
  ([PR #25](https://github.com/MSKazemi/aobench/pull/25)). Those tests then caught a
  ranking bug in the maintainer's own overlapping implementation, which is why
  `aobench run task --task JOB_USR_00` suggests `JOB_USR_001` today.

- **Barshana Chatterjee** ([@Barshana24](https://github.com/Barshana24)) — took
  [issue #29](https://github.com/MSKazemi/aobench/issues/29) and gave `report json` and
  `compare runs` a `--json` flag, so AOBench can be wired into CI without scraping
  formatted tables ([PR #43](https://github.com/MSKazemi/aobench/pull/43)). Also spotted
  that the issue named a `report summary` command that does not exist, and said so
  instead of inventing one. Came back for
  [issue #28](https://github.com/MSKazemi/aobench/issues/28) and built
  `aobench list coverage`, which turns "where is this benchmark thin?" from a shell
  pipeline over filenames into one command
  ([PR #47](https://github.com/MSKazemi/aobench/pull/47)) — and, told not to parse
  filenames, worked out for herself *why*: the `M100_` tasks carry an extra ID segment
  that shifts every position after it. The design call on how to count those tasks was
  hers, made and defended before anyone asked.

- **LeoZhaoo** ([@LobsterQBA](https://github.com/LobsterQBA)) — took
  [issue #31](https://github.com/MSKazemi/aobench/issues/31) and wrote
  `examples/05_compare_two_adapters.py`, the side-by-side comparison the benchmark exists
  for and the one thing the first four examples never showed
  ([PR #44](https://github.com/MSKazemi/aobench/pull/44)). It reuses `aobench compare runs`
  rather than re-deriving the deltas, and registers itself in the example smoke tests, so
  the README's promise that a broken example breaks the build stays true.

- **Atiqur Rahman** ([@atiqur-rahman-pro](https://github.com/atiqur-rahman-pro)) — noticed
  that `scripts/` was the one Python directory sitting outside every quality gate, and did
  the unglamorous read across 31 of its files
  ([PR #45](https://github.com/MSKazemi/aobench/pull/45)). Those 55 scripts generate the
  docs catalogs, the RBAC policy pages and the frozen paper tables, so `ruff check` now
  covers them in CI. Narrowing their blanket `except Exception` handlers also exposed a
  latent crash in the tool-docs generator that an empty `metadata.yaml` had been able to
  abort since the script was written. Then split a second finding out of that PR rather
  than burying it in it: the rubric reliability gate computed `ICC1` while its docstring,
  its error message, the docs and its own test module all said `ICC(A,1)` — two different
  statistics under one name ([PR #46](https://github.com/MSKazemi/aobench/pull/46)). The
  gate is dormant until multi-judge scoring is switched on, which makes this the cheapest
  moment it could possibly have been caught.

<!-- Add yourself in your first PR: - **Your Name** (@handle) — what you contributed -->

## Acknowledgements

- **CINECA** for publishing the Marconi100 **ExaData** release, which is what lets six
  of AOBench's environments be grounded in real Tier-0 operational data rather than
  invented. A benchmark of this kind is only as credible as the real data underneath
  it.
- The authors of **BFCL**, **τ-bench**, **SWE-bench**, and **TRAIL**, whose evaluation
  designs AOBench borrows from directly and cites in
  [related work](https://mskazemi.com/aobench/latest/about/related-work/).

## Recognition policy

- **Code, docs, tests, corpus, and review** all count. Reviewing someone else's PR
  carefully is a contribution, and it gets listed.
- **Release notes name contributors** for the version their change shipped in.
- **Substantial corpus or methodological contributions may warrant co-authorship** on a
  paper that depends on them. If you believe that applies to your work, say so — the
  awkwardness of asking should not decide who gets credit.
- **Contributions stay listed** even if you later step away.

To add yourself, edit this file in the same PR as your change. If you would rather not
be listed, that is fine too — just say so in the PR.
