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

```powershell
npx --yes github:mitunmanav/everything-ai
```

Dry run:

```powershell
npx --yes github:mitunmanav/everything-ai -- --dry-run
```

Claude install target:

```powershell
npx --yes github:mitunmanav/everything-ai -- --agent claude
```

Use after install:

```txt
Use $everything-ai and do everything for this task.
```

The installer copies only `skills/everything-ai`, sends no telemetry, reads no secrets, and refuses overwrite unless `--force` is used.

Default install target is Codex/OpenAI. Use `--agent claude` for Claude.

## v0.3.0 Status

v0.3.0 is a proof release draft. It is useful, but not final.

- local tests: passed
- skill validation: passed
- plugin evaluation: 100/100, Grade A, low risk
- behavior comparison: with skill 20/20, without skill 14/20, delta +6
- domain-pack comparison: with packs 24/24, without packs 18/24, delta +6
- model: `gpt-5.4-mini`, medium reasoning
- test method: saved-output regression suite from fresh subagent scorecard
- CI workflow: runs on pushes and pull requests
- agent metadata: OpenAI/Codex and Claude
- domain packs: startup, data analysis, personal productivity
- raw result: [`tests/results/v0.3.0-with-vs-without-skill.json`](tests/results/v0.3.0-with-vs-without-skill.json)

![Everything AI v0.3.0 behavior lift](tests/results/v0.3.0-with-vs-without-skill.svg)

Known gaps:

- no real usage logs yet
- no coverage artifact yet
- benchmark runner is saved-output based, not live model execution yet
- public GitHub release is still v0.2.0 until explicit approval

More detail: [`TEST_RESULTS.md`](TEST_RESULTS.md), [`EVALUATION.md`](EVALUATION.md), [`ROADMAP.md`](ROADMAP.md).

## Domain Packs

Domain packs live in `skills/everything-ai/domains/`.

Each pack must use this format:

- `## Scope Defaults`
- `## Checklist`
- `## Pitfalls`
- `## Success Looks Like`
- `## Examples` with `Example 1` and `Example 2`

Current packs:

- `startup.md`
- `data-analysis.md`
- `personal-productivity.md`

Saved domain-pack comparison: [`tests/results/v0.3.0-domain-pack-comparison.json`](tests/results/v0.3.0-domain-pack-comparison.json)

## Privacy

v0.3.0 public files must not include local paths, local machine names, emails, tokens, secrets, private thread IDs, or private user details.

Project tests scan public docs for local-only path and identity leaks.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=mitunmanav/everything-ai&type=Date)](https://www.star-history.com/#mitunmanav/everything-ai&Date)
