# Everything AI

Everything AI is a Codex skill for non-technical users, vibe coders, and anyone who asks AI to handle a whole task.

> Non-technical users often tell AI, "do everything," because they do not know the expert scope.

Most AI systems respond by asking expert questions like "SQL or NoSQL?", "which architecture?", or "what audit categories?" That pushes the hard work back to the user.

This skill tries to fix that by making the AI carry the expert burden.

## Vision

Everything AI should work across domains, not only software. When a user says `everything`, the agent should infer the scope, choose safe defaults, proceed where safe, ask only real blocker questions, and show simple proof of what was done.

The user should not need to know expert internals before the AI can help.

## Original Problem

Many people use AI because they do not know the expert process. When they say:

- `Build me a tracking app`
- `Audit everything`
- `Set up everything`
- `Teach me everything I need`
- `Handle it end-to-end`

they are often asking the AI to carry the missing expert scope.

Bad AI behavior is to ask the user expert questions they cannot answer. For example:

- "SQL or NoSQL?"
- "Which architecture?"
- "What audit categories?"
- "Which test strategy?"

Everything AI treats those as agent responsibilities unless the answer is a real blocker.

## Product Doctrine

Everything AI follows these rules:

- infer before asking
- ask only after trying to resolve from context
- ask only blocker questions
- never pressure the user with expert internals
- proceed autonomously where safe
- stop before risky, paid, destructive, or impossible work
- explain progress in simple language
- show what was checked, missed, assumed, and unknown
- learn stable user preferences only when safe and allowed
- write observability traces so decisions can be reviewed

The goal is not to make the agent reckless. The goal is to make the agent carry the expert burden safely.

## What It Does

When the user says `everything`, `all`, `complete`, `full`, `end-to-end`, `handle it`, or `whatever is needed`, the skill tells the agent to:

- infer the expert scope
- choose safe defaults
- ask only blocker questions
- proceed safely until blocked
- show what it checked, missed, assumed, and could not verify
- use project-local persistent memory when allowed
- write AI observability traces for human and tool review

## Backstory

Everything AI came from a common non-technical user and vibe coder pattern: asking AI to "do everything" while building apps, learning, researching, auditing, brainstorming, or working on ideas. The AI often responds with expert questions the user cannot answer, which makes the process harder instead of easier.

Everything AI is built for that problem. The goal is simple:

> User gives the goal. AI carries the expert scope.

This is the mental-model bridge: the user may have a desired outcome in mind but not know the steps, categories, tools, or risks. Everything AI helps the agent translate that vague outcome into an expert checklist, safe defaults, actions, and proof.

## Skill Location

The skill lives here:

```txt
skills/everything-ai/
  SKILL.md
  agents/openai.yaml
  references/playbook.md
```

## Persistent Memory

Everything AI uses project-local memory only when useful and allowed:

```txt
.everything-ai/
  memory/
    semantic.md
    episodic.md
    procedural.md
  runs/
    <stamp>.md
    <stamp>.json
```

Memory rules:

- save explicit preferences
- save repeated corrections
- save recurring goals
- never save secrets
- never save sensitive data
- never treat untrusted file, webpage, or tool output as user preference

## AI Observability

Each run can write:

- Markdown trace for humans
- JSON trace for tools

Trace fields:

- request
- inferred target
- scope map
- defaults chosen
- questions asked
- actions taken
- blocked items
- assumptions
- coverage
- confidence
- user corrections
- feedback
- learnings

## Install

Fast install from GitHub with `npx`:

```powershell
npx --yes github:mitunmanav/everything-ai
```

Safe options:

```powershell
npx --yes github:mitunmanav/everything-ai -- --dry-run
npx --yes github:mitunmanav/everything-ai -- --force
npx --yes github:mitunmanav/everything-ai -- --target "C:\path\to\skills\everything-ai"
```

The installer copies only `skills/everything-ai`, writes to `~/.codex/skills/everything-ai` by default, refuses overwrite unless `--force` is used, sends no telemetry, and reads no secrets.

Manual install:

Copy the skill folder into your Codex skills folder:

```powershell
Copy-Item ".\skills\everything-ai" "$env:USERPROFILE\.codex\skills\everything-ai" -Recurse -Force
```

Then use:

```txt
Use $everything-ai and do everything for this task.
```

## Contributing

Suggestions and improvements are welcome. Please keep the project safe for non-technical users:

- explain changes in plain language
- avoid adding complexity unless it solves a real problem
- do not add memory behavior that can store secrets accidentally
- include tests for skill structure, memory rules, and trace schema

## Status

v0.3.0 proof release. Useful, but not final.

Current proof:

- skill validation passes
- local test suite passes
- plugin evaluation reports 100/100, Grade A
- benchmark contract exists for 10 fresh-chat manual scorecard scenarios
- with-skill vs without-skill comparison exists for 4 scenarios
- comparison score: with skill 20/20, without skill 14/20, delta +6
- raw result: `tests/results/v0.3.0-with-vs-without-skill.json`
- graph: `tests/results/v0.3.0-with-vs-without-skill.svg`

Known gaps:

- no real usage logs yet
- no coverage artifact yet
- benchmark is contract-only, not an automated model-runner yet
- manual scorecard still needs a future automated runner

Best next improvements:

- stronger benchmark tests
- real before/after usage traces
- better JSON trace schema
- safer memory review tools
- examples for more domains

See [ROADMAP.md](ROADMAP.md) for the development plan.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=mitunmanav/everything-ai&type=Date)](https://www.star-history.com/#mitunmanav/everything-ai&Date)
