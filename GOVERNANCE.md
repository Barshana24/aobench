# Governance

How AOBench is run, who decides what, and how you get a say. This document exists so
that "who decides?" never has to be answered by guessing.

## Project structure

AOBench is a small, academically-hosted open-source project maintained at the
Department of Electrical, Electronic and Information Engineering (DEI), University of
Bologna. It uses **BDFL-with-a-published-process** governance: the maintainers decide,
but the criteria are written down and the reasoning is public.

We are not pretending to be a foundation. If the project grows to the point where this
model stops being honest, this document changes first.

## Roles

### Users
Anyone who runs AOBench. You can open issues, ask questions in Discussions, and expect
a response. You do not need permission to use, fork, or publish results.

### Contributors
Anyone whose patch has been merged. You are listed in `AUTHORS.md` and in the release
notes for the version your change shipped in. No CLA is required — Apache-2.0 inbound
equals outbound.

### Maintainers
Listed in [MAINTAINERS.md](MAINTAINERS.md). Maintainers can merge PRs, cut releases,
and change the corpus. They are accountable for the correctness of the benchmark, which
in practice means being the people who have to be convinced a gold answer is right.

## Becoming a maintainer

There is no secret process and no minimum commit count. The criteria:

1. **Sustained, quality contribution** — roughly three months of meaningful work, and
   more importantly a track record of changes that did not need to be reworked.
2. **Review judgement** — you have reviewed others' PRs and caught real problems.
3. **Domain care** — for corpus areas, you have shown you will argue about whether a
   gold answer is actually right rather than waving it through.
4. **Agreement from existing maintainers**, decided in a public discussion.

If you want this, say so — it is a reasonable thing to want and asking is not
presumptuous. Maintainers can also step back to emeritus at any time, with no drama and
no explanation owed.

## Decision-making

| Decision | Process |
|---|---|
| Bug fix, docs, tests, examples | One maintainer approval. Just send the PR. |
| New CLI flag, new adapter, new task or environment | One maintainer approval; open an issue first only if the design is unclear |
| Change to the task schema, scoring weights, or RBAC model | Public issue, at least 7 days for comment, maintainer consensus |
| Anything that invalidates published scores | As above, **plus** an explicit entry in `CHANGELOG.md` under a score-affecting heading |
| Removing or relabelling a task | Public issue; the task ID is never reused |
| Release | Any maintainer, following the release checklist |
| Governance change | Public issue, 14 days, maintainer consensus |

**Disagreement is resolved by discussion, then by the maintainers, and the reasoning is
written in the issue.** If you think a decision was wrong, saying so in the issue is
welcome; re-litigating it in five other threads is not.

## Scientific integrity commitments

These are the ones that matter for a benchmark, and they bind the maintainers too:

1. **Wrong gold answers are bugs, not opinions.** A credible report that a gold answer
   is incorrect is high priority regardless of who reports it or how inconvenient the
   timing is.
2. **We publish corrections loudly.** If a change invalidates numbers we ourselves have
   published, that goes in the release notes' first paragraph, not a footnote.
3. **No score is changed silently.** Every scoring change is versioned and recorded —
   see [the versioning policy](https://mskazemi.com/aobench/latest/about/versioning/).
4. **The held-out split stays held out.** Test-split tasks are not shown, not used in
   public leaderboards, and not tuned against.
5. **Maintainers' own results get the same scrutiny.** If we publish an AOBench number,
   it meets the same submission requirements we ask of everyone else.

## Conflicts of interest

Maintainers who are involved with an agent or model being evaluated must say so on any
issue or PR touching that evaluation, and should not be the sole approver of a
leaderboard submission for it. This is not an accusation of anything; it is what makes
the numbers worth reading.

## Code of conduct

The [Code of Conduct](CODE_OF_CONDUCT.md) applies to every project space. Enforcement
is by the maintainers; reports go to the contact address listed there.

## Funding and independence

AOBench is university research output. It takes no vendor money, and no organisation
has the right to influence which agents score well or which tasks exist. If that ever
changes, it will be disclosed here before it takes effect.

## Forking

Apache-2.0. Fork it. If you fork because the project is not going where you need, we
would rather hear why first — but the licence is the guarantee, not our goodwill.
