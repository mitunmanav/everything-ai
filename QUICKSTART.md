# Quick Start — Everything AI

## What it does

Tell it anything. It figures out what you need, makes sensible choices, and gets to work.

You do not need to know what kind of AI task this is. Just say what you want in plain language.

## How to use it

**In Codex:** Type `$everything-ai` then describe what you want.

**In Claude:** Type `/everything-ai` then describe what you want.

**Or just say:** "Do everything for [your task]" or "Handle everything" or "I need help with everything related to [topic]."

## Examples

Just say things like:

- "Do everything to launch my startup idea"
- "Help me get fit — I'm a complete beginner"
- "Fix the bug in my code"
- "Write an email to my landlord about the broken heater"
- "Make a plan for learning Python in one month"
- "Research the best budget laptops under $500"
- "Help me organize my finances — I don't know where to start"
- "Plan my move to a new city"
- "I need to write a blog post about remote work"
- "Help me study for my exam"

## What it will do

1. Understand what you probably mean
2. Tell you what it's assuming (one sentence)
3. Do the work
4. Tell you what it did, what it needs from you, and what it's not sure about

## When it will ask you a question

Only when it truly cannot proceed without your answer. At most one question per task.

It will never ask you to choose between technical options you don't understand.

## Install

```bash
npm install -g everything-ai
node -e "require('everything-ai/scripts/install.js')" -- --agent codex
```

Or for Claude:

```bash
node -e "require('everything-ai/scripts/install.js')" -- --agent claude
```
