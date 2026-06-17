# Everything AI

Everything AI is a Codex skill for one common problem:

> Non-technical users often tell AI, "do everything," because they do not know the expert scope.

Most AI systems respond by asking expert questions like "SQL or NoSQL?", "which architecture?", or "what audit categories?" That pushes the hard work back to the user.

This skill tries to fix that.

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

Everything AI came from a common non-technical user pattern: asking AI to "do everything" while building apps or working on ideas. The AI often responds with expert questions the user cannot answer, which makes the process harder instead of easier.

Everything AI is built for that problem. The goal is simple:

> User gives the goal. AI carries the expert scope.

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

Early public version. Useful, but not final. Best next improvements:

- stronger benchmark tests
- real before/after usage traces
- better JSON trace schema
- safer memory review tools
- examples for more domains
