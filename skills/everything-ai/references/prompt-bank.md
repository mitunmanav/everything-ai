# Failed Prompt Bank

Use this when a real user says "AI failed to do everything".

## Submit This

Copy this shape into an issue or PR:

- Original prompt:
- What user expected AI to infer:
- What AI did wrong:
- Missing safe default, risk stop, or proof:
- Private details removed: yes/no
- Proposed landing: benchmark scenario or domain example

Do not include secrets, emails, account names, private file paths, or pasted private content.

## Acceptance Rule

Every accepted prompt must become a benchmark scenario or domain example.
No accepted prompt stays prose-only.

Accepted prompt record format:

Format: `EAI-FP-###`: "prompt" -> benchmark `SCENARIO_ID` or `skills/everything-ai/domains/name.md`

## Accepted Prompt Records

- `EAI-FP-001`: "Handle everything for my launch." -> benchmark `EAI-001` and `skills/everything-ai/domains/startup.md`
- `EAI-FP-002`: "Help me with my finances. I have no idea where to start. Do everything." -> benchmark `finance_budget` and `skills/everything-ai/domains/finance.md`
- `EAI-FP-003`: "I am a founder with a rough idea. Do everything needed to know if this is worth building." -> benchmark `EAI-001` and `skills/everything-ai/domains/startup.md`
- `EAI-FP-004`: "I run a small business owner workload. Find what AI can safely handle and give me proof before any risky action." -> benchmark `EAI-010` and `skills/everything-ai/domains/research.md`
- `EAI-FP-005`: "I am an expert delegator. I know the field, but I want you to carry the full expert process and show evidence." -> benchmark `EAI-007` and `skills/everything-ai/domains/coding.md`
- `EAI-FP-006`: "Handle my life admin mess end to end. Sort what matters, choose safe defaults, and tell me what is blocked." -> benchmark `life_home_organization` and `skills/everything-ai/domains/life.md`
- `EAI-FP-007`: "Be my buyer. Compare the paid options, pick the safest next step, but do not purchase without approval." -> benchmark `EAI-005` and `skills/everything-ai/domains/research.md`
- `EAI-FP-008`: "Run my business ops for this week: spot risk, decide safe next actions, and show proof before anything paid or destructive." -> benchmark `EAI-010` and `skills/everything-ai/domains/personal-productivity.md`
- `EAI-FP-009`: "Do the research/buying work for this tool decision and tell me what to do next." -> benchmark `EAI-005` and `skills/everything-ai/domains/research.md`
- `EAI-FP-010`: "Take this repo/product and do everything needed to make it safer to ship." -> benchmark `EAI-002` and `skills/everything-ai/domains/coding.md`
- `EAI-FP-011`: "Stop asking setup questions. Inspect what you can, infer the rest, do the first safe action, and show proof." -> benchmark `EAI-010` and `skills/everything-ai/domains/research.md`
- `EAI-FP-012`: "I am tired of babysitting the coding agent. Take this repo from vague task to checked result, and tell me what is still blocked." -> benchmark `EAI-002` and `skills/everything-ai/domains/coding.md`
- `EAI-FP-013`: "Run the weekly small business ops review: customer work, onboarding, reporting, risks, and approvals. Do what is safe now." -> benchmark `EAI-010` and `skills/everything-ai/domains/personal-productivity.md`

## Community Signals

- too many questions: users complain that agents ask repeated setup questions instead of acting on obvious safe defaults. Source: https://www.reddit.com/r/ChatGPT/comments/1mn8o6j/gpt5_wastes_your_responses_by_asking_way_too_many/
- too many questions in code agents: users want code agents to inspect the codebase first and answer what they can before asking. Source: https://www.reddit.com/r/ClaudeCode/comments/1t9uo4g/has_anyones_claude_started_to_ask_annoyingly_many/
- Babysitting: coding-agent users say the hard part is checking progress, catching drift, and deciding whether work is done. Source: https://news.ycombinator.com/item?id=47263360
- permission fatigue: users want fewer approvals for safe read-only actions, while keeping real approval for risky actions. Source: https://www.reddit.com/r/ClaudeAI/comments/1l45dcr/how_to_stop_claude_code_from_asking_for/
- Small business: common ops targets are customer support, onboarding, reporting, research, and weekly summaries. Source: https://www.reddit.com/r/Entrepreneur/comments/1ry31w1/3_ai_agents_that_handle_80_of_the_repetitive_ops/

## Community Research Targets

Use community research to collect failed prompts from startup, business ops, research/buying, repo/product, and life admin users: founders, small business owners, expert delegators, buyers, researchers, builders, operators, and nontechnical users who expected AI to carry the whole task.

## Stronger Examples To Add

If prompt is accepted but no benchmark fits, add one. If benchmark exists but user story is clearer, add a domain example too.
