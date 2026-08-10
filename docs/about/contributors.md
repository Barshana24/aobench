# Contributors

**Thank you.** AOBench is a benchmark, which means its value is not in the code — it is in
how carefully the 88 tasks, the 29 environments, the scoring rules, and the documentation
have been checked by people who were not the person who wrote them. Every fix, every
question that exposed an unclear page, every "this crashed for me" is that checking. This
page is where those people are named.

## Maintainers

<ul class="wall">
<li>
  <span class="wall-avatar">
    <img src="https://github.com/MSKazemi.png?size=144" alt="" loading="lazy">
    <span class="wall-badge" aria-hidden="true">🛠️</span>
  </span>
  <span class="wall-name">Mohsen Seyedkazemi Ardebili</span>
  <span class="wall-handle"><a href="https://github.com/MSKazemi">@MSKazemi</a></span>
  <span class="wall-role">Maintainer</span>
  <span class="wall-tag">Benchmark, scorers, corpus</span>
</li>
<li>
  <span class="wall-avatar">
    <span class="wall-initials" aria-hidden="true">AB</span>
    <span class="wall-badge" aria-hidden="true">🎓</span>
  </span>
  <span class="wall-name">Andrea Bartolini</span>
  <span class="wall-handle"><a href="https://orcid.org/0000-0002-1148-2450">ORCID</a></span>
  <span class="wall-role">Maintainer</span>
  <span class="wall-tag">Scientific direction</span>
</li>
</ul>

Both at the Department of Electrical, Electronic and Information Engineering (DEI),
University of Bologna.

## Contributors

Listed in the order their first contribution merged. The badge on each avatar marks what
they worked on; the line underneath says it in words.

<ul class="wall">
<li>
  <span class="wall-avatar">
    <img src="https://github.com/erensh27.png?size=144" alt="" loading="lazy">
    <span class="wall-badge" aria-hidden="true">🧭</span>
  </span>
  <span class="wall-name">abhinav</span>
  <span class="wall-handle"><a href="https://github.com/erensh27">@erensh27</a></span>
  <span class="wall-role">First contributor</span>
  <span class="wall-tag">Friendly CLI errors</span>
</li>
<li>
  <span class="wall-avatar">
    <img src="https://github.com/Barshana24.png?size=144" alt="" loading="lazy">
    <span class="wall-badge" aria-hidden="true">🔌</span>
  </span>
  <span class="wall-name">Barshana Chatterjee</span>
  <span class="wall-handle"><a href="https://github.com/Barshana24">@Barshana24</a></span>
  <span class="wall-role">Contributor</span>
  <span class="wall-tag">Machine-readable output</span>
</li>
<li>
  <span class="wall-avatar">
    <img src="https://github.com/LobsterQBA.png?size=144" alt="" loading="lazy">
    <span class="wall-badge" aria-hidden="true">⚖️</span>
  </span>
  <span class="wall-name">LeoZhaoo</span>
  <span class="wall-handle"><a href="https://github.com/LobsterQBA">@LobsterQBA</a></span>
  <span class="wall-role">Contributor</span>
  <span class="wall-tag">Side-by-side comparison</span>
</li>
</ul>

### 🧭 [@erensh27](https://github.com/erensh27) — friendly CLI errors

AOBench's first external contributor. They took
[issue #2](https://github.com/MSKazemi/aobench/issues/2) and replaced the raw Python
traceback you used to get from a mistyped `--task` or `--env` with an actionable one-line
error, and — this is the part that matters — wrote end-to-end CLI tests for it. Those tests
then failed against the maintainer's own overlapping implementation and exposed a real
ranking bug in it: `aobench run task --task JOB_USR_00` was answering *"did you mean
JOB_USR_005, JOB_USR_004, JOB_USR_003?"* and silently omitting `JOB_USR_001`. It suggests
`JOB_USR_001` today because of [PR #25](https://github.com/MSKazemi/aobench/pull/25).

That is the whole argument for outside contributors in one example: a second person's test
found something the author's own tests were structurally unable to see.

### 🔌 [@Barshana24](https://github.com/Barshana24) — machine-readable output

Took [issue #29](https://github.com/MSKazemi/aobench/issues/29) and gave `aobench report
json` and `aobench compare runs` a `--json` flag, so the two commands that produce AOBench's
numbers can be piped into `jq` instead of scraped as formatted text
([PR #43](https://github.com/MSKazemi/aobench/pull/43)). For a benchmark whose whole value
is machine-comparable numbers, that closed a real gap.

They also noticed that the issue named a `report summary` command that does not exist, put
the flag where the logic actually lives, and said so — instead of quietly inventing a
command to match the issue title. That judgement saved a bad API.

### ⚖️ [@LobsterQBA](https://github.com/LobsterQBA) — side-by-side comparison

Took [issue #31](https://github.com/MSKazemi/aobench/issues/31) and wrote
[`examples/05_compare_two_adapters.py`](https://github.com/MSKazemi/aobench/blob/main/examples/05_compare_two_adapters.py),
the comparison this benchmark exists for and the one thing the first four examples never
showed: two systems side by side, with the per-dimension deltas rather than a single
headline score ([PR #44](https://github.com/MSKazemi/aobench/pull/44)).

It reuses `aobench compare runs` rather than re-deriving the deltas, so the examples cannot
drift from the CLI, and it registers itself in the example smoke tests — which keeps the
examples README's promise that a broken example breaks the build rather than quietly
rotting. It runs offline, with no API key.

### In review right now

[@atiqur-rahman-pro](https://github.com/atiqur-rahman-pro) is working through
[issue #6](https://github.com/MSKazemi/aobench/issues/6), the lint debt in `scripts/`. While
doing it he found something nobody had noticed: the rubric scorer computes one
intraclass-correlation statistic while its docstrings, its error messages, this
documentation and its tests all name a different one. That is a real methodology bug in the
benchmark, found by someone who was only supposed to be tidying imports — and it is exactly
why this page exists.

## How you get on this wall

Every merged contribution earns a place here, whatever its size. A typo fix in the docs is
a real contribution to a project whose documentation *is* the product.

| If you want to… | Start here |
|---|---|
| Fix something small and well-specified | [Good first issues](https://github.com/MSKazemi/aobench/labels/good%20first%20issue) — each names the files, the tests, and an honest time estimate |
| Improve a page that confused you | Edit it directly; the pencil icon at the top of every page opens a PR |
| Report a bug or request a feature | [Open an issue](https://github.com/MSKazemi/aobench/issues/new/choose) |
| Propose a task or an environment | [Contributing guide](contributing.md) |
| Ask something | [Discussions](https://github.com/MSKazemi/aobench/discussions) — questions are welcome and expected |

You do not need HPC access or a cluster. The whole benchmark runs against frozen snapshots
on a laptop, and the `direct_qa` adapter needs no API key.

## What recognition means here

- **Code, docs, tests, corpus, and review all count.** Reviewing someone else's PR
  carefully is a contribution, and it gets listed.
- **Release notes name contributors** for the version their change shipped in, and the
  [changelog](changelog.md) links the person next to the fix.
- **Substantial corpus or methodological contributions may warrant co-authorship** on a
  paper that depends on them. If you think that applies to your work, say so — the
  awkwardness of asking should not be what decides who gets credit.
- **Contributions stay listed** even if you later step away.
- **You can decline.** If you would rather not appear here, say so in the PR and you won't.

## What you can expect from us

A first response within three working days, even when that response is only "seen, I'll
look properly on Friday". If a PR of yours goes quiet for longer, ping it — that is our
failure, not rudeness on your part.

We hold ourselves to that publicly because we have already missed it: PR #25 sat for a day
while an overlapping implementation was written and merged in parallel, which is the one
thing a maintainer most owes a contributor not to do. The [rework of that
PR](https://github.com/MSKazemi/aobench/pull/25) preserves the contributor's commits and
credit precisely because the mistake was ours.

## Acknowledgements

- **CINECA**, for publishing the Marconi100 **ExaData** release, which is what lets six of
  AOBench's environments be grounded in real Tier-0 operational data rather than invented.
  A benchmark of this kind is only as credible as the real data underneath it.
- The authors of **BFCL**, **τ-bench**, **SWE-bench**, and **TRAIL**, whose evaluation
  designs AOBench borrows from directly and cites in [related work](related-work.md).

---

The canonical, machine-readable record of everyone listed here is
[`AUTHORS.md`](https://github.com/MSKazemi/aobench/blob/main/AUTHORS.md) in the repository
root; this page is its presentation. Author metadata for citation purposes lives in
[`CITATION.cff`](https://github.com/MSKazemi/aobench/blob/main/CITATION.cff) — see
[Cite AOBench](citation.md).
