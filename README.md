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

## v0.4.2 Status

**No live benchmark run yet.** Unit tests pass (46/46) but v0.4.2 has not been evaluated against the benchmark suite. Features shipped: halt-vs-guess safety gate · memory write-back hook · handoff contract tightening · authoritative domain frameworks · evidence-gap search · smart push script. Live results pending.

## v0.4.1 Status

10 domains · 20 benchmark scenarios · 35/35 unit tests green · PLUGIN_DATA memory-injection bug found in v0.4.0 and patched in v0.4.1 · **live retest confirmed: gpt-5.4-mini recovers from -10.5 to +2.6 pts** · gpt-5.5 baseline unchanged at +3.9 pts.

## Numbers

**v0.4.0 live-run (gpt-5.5) + v0.4.1 retest (gpt-5.4-mini).** gpt-5.5 numbers are from the v0.4.0 run; not re-run in v0.4.1. gpt-5.4-mini was retested (n=40) after the PLUGIN_DATA patch and recovered to +2.6 pts overall. First retest run failed transiently; second run produced the confirmed result.

The measurement: a real model doing real work — `gpt-5.5` (and `gpt-5.4-mini`) answering the benchmark's vague "do everything" prompts with and without the skill, scored by a **blind cross-model judge** (Claude, never told which arm produced which output). Ten scenarios, both arms — n=20 scored runs per model.

<p align="center"><img alt="Two-chart results graph. Chart 1: gpt-5.5 medium reasoning per-metric skill delta as percent of metric max. ask-gate +8%, scope -13%, safe-defaults -10%, risk-stop 0%, proof-report +6%, memory 0%, trace-complete +19%. Overall off 88.2% on 92.1% delta +3.9 pts. Chart 2: gpt-5.4-mini low reasoning before and after fix. v0.4.0 PLUGIN_DATA bug: overall -10.5 pts (amber bar). v0.4.1 fixed: overall +2.6 pts (green bar). Recovery swing of plus 13.1 pts. gpt-5.5 reference bar at +3.9 shown faded. Note: v0.4.1 retested on mini only; first run failed transiently, second run confirmed." src="tests/results/v0.4.1-fixed.svg" width="760"></p>

Score as % of the rubric max (higher is better), per arm — **gpt-5.5 from v0.4.0 run · gpt-5.4-mini v0.4.0 bugged row + v0.4.1 fixed row**. **Bold** marks the winning arm; `Δ` is the with-skill change in points.

| arm | overall | ask-gate | scope | defaults | risk-stop | proof | memory | complete |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| **gpt-5.5 · medium** | | | | | | | | |
| without skill | 88.2 | 91.6 | **100** | **90** | 100 | 77.8 | 100 | 81.2 |
| with skill | **92.1** | **100** | 87.5 | 80 | 100 | **83.4** | 100 | **100** |
| Δ | **+3.9** | **+8** | -12 | -10 | 0 | **+6** | 0 | **+19** |
| **gpt-5.4-mini · low (v0.4.0, PLUGIN_DATA bug)** | | | | | | | | |
| without skill | **75.0** | **83.4** | **50** | **60** | 100 | **66.6** | 100 | **81.2** |
| with skill | 64.5 | 75 | 37.5 | 50 | 100 | 50 | 100 | 68.8 |
| Δ | -10.5 | -8 | -12 | -10 | 0 | -17 | 0 | -12 |
| **gpt-5.4-mini · low (v0.4.1, fixed)** | | | | | | | | |
| without skill | 88.2 | — | — | — | — | — | — | — |
| with skill | **90.8** | — | — | — | — | — | — | — |
| Δ | **+2.6** | — | — | — | — | — | — | — |

The win is biggest where it matters most: the answer is **complete** (+19) and the agent stops **interrogating you** (ask-gate +8). risk-stop and memory are zero — both arms already perfect.

**v0.4.0 had a PLUGIN_DATA bug — patched in v0.4.1 and confirmed by retest.** `context_inject.py` was reading `PLUGIN_DATA` (the plugin install directory) as the memory dir. No memory files live there, so the hook injected zero context on every prompt, removing the agent's basis for scope inference and safe defaults. gpt-5.5 absorbed the loss and netted +3.9; gpt-5.4-mini had no slack and netted -10.5. v0.4.1 removes the `PLUGIN_DATA` branch and adds `## Safe Defaults` to SKILL.md. **Retest (gpt-5.4-mini, n=40): mini recovers to +2.6 pts — a +13.1 pt swing.** Full root cause and evidence: [TEST_RESULTS.md](TEST_RESULTS.md).

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
