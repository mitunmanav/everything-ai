# Everything AI

[![test](https://github.com/mitunmanav/everything-ai/actions/workflows/test.yml/badge.svg)](https://github.com/mitunmanav/everything-ai/actions/workflows/test.yml)

Everything AI is an agent skill for people who ask AI to handle the whole task.

It is built for non-technical users, vibe coders, and broad requests like:

- `do everything`
- `handle it end-to-end`
- `audit everything`
- `set up the whole thing`
- `whatever is needed`

Most agents ask expert questions too early. Everything AI tells the agent to infer scope, choose safe defaults, act where safe, and ask only real blocker questions.

## What It Does

When triggered, the skill pushes the agent to:

- infer the missing expert checklist
- start with safe defaults
- avoid dumping expert choices on the user
- stop before paid, destructive, private, medical, legal, or unsafe actions
- show what was checked, assumed, missed, and still unknown
- write reviewable trace fields when memory or observability is useful

Short version:

> User gives goal. AI carries expert scope.

## Install

Default (Codex/OpenAI):

```powershell
npx --yes github:mitunmanav/everything-ai
```

Dry run:

```powershell
npx --yes github:mitunmanav/everything-ai -- --dry-run
```

Claude:

```powershell
npx --yes github:mitunmanav/everything-ai -- --agent claude
```

Use after install:

```txt
Use $everything-ai and do everything for this task.
```

The installer copies only `skills/everything-ai`, sends no telemetry, reads no secrets, and refuses overwrite unless `--force` is used.

Default install target is Codex/OpenAI. Use `--agent claude` for Claude.

## v0.4.0 Status

10 domains · 20 benchmark scenarios · 32/32 tests green · +3.9pt behavior lift on a capable model.

## Numbers

The honest measurement is a real model doing real work: `gpt-5.5` (and a smaller `gpt-5.4-mini`) answering the benchmark's vague "do everything" requests in a neutral scratch dir, with and without the skill, scored on the answer it leaves behind by a **blind cross-model judge** (Claude, never told which arm produced which output). Ten scenarios carry the rubric, scored under both arms — n=20 scored runs per model.

![Behavior quality with vs without the skill, two models, blind cross-model judge](tests/results/v0.4.0-all-phases.svg)

| with skill vs without | overall | complete | ask-gate | proof | scope | defaults |
|---|--:|--:|--:|--:|--:|--:|
| **gpt-5.5 · medium** | **+3.9** | **+19** | **+8** | **+6** | -12 | -10 |
| gpt-5.4-mini · low | -10.5 | -12 | -8 | -16 | -12 | -10 |

Numbers are percentage points of the rubric max (higher is better). On a capable model the skill is a real, modest win — it makes the answer **complete** and stops the agent **interrogating you**, with a small cost on raw scope/defaults that the model already handles. On a small low-reasoning model the same instructions **overload it** and every metric drops: the skill is built for capable models. Full method, per-metric tables, reran failures, and limitations: [TEST_RESULTS.md](TEST_RESULTS.md).

Details: [QUICKSTART.md](QUICKSTART.md) · [TEST_RESULTS.md](TEST_RESULTS.md) · [ROADMAP.md](ROADMAP.md)

## Domain Packs

Domain packs live in `skills/everything-ai/domains/`.

Each pack has five sections: `Scope Defaults`, `Checklist`, `Pitfalls`, `Success Looks Like`, `Examples`.

Current packs (10 total):

| Pack | What it handles |
|---|---|
| `startup.md` | Founder, MVP, launch, business idea |
| `data-analysis.md` | CSV, spreadsheet, metrics, dashboard |
| `personal-productivity.md` | Tasks, notes, schedule, planning |
| `coding.md` | Bugs, refactors, builds, deploys |
| `writing.md` | Drafts, edits, emails, essays |
| `health.md` | Fitness, diet, sleep, wellness |
| `learning.md` | Courses, skills, study plans |
| `finance.md` | Budget, debt, savings, investing |
| `life.md` | Home, family, chores, moves |
| `research.md` | Compare, investigate, summarize |

## Privacy

Public files contain no local paths, machine names, emails, tokens, secrets, or private user details. Tests scan for leaks before every commit.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=mitunmanav/everything-ai&type=Date)](https://www.star-history.com/#mitunmanav/everything-ai&Date)
