# Contributing

Thank you for helping improve Everything AI.

This project is for people who say "do everything" because they want AI to carry the expert scope. Keep that user in mind.

Do not add mode menus or process choices the user has to manage. Everything AI should infer, act safely, verify, and report proof.

## Good Contributions

- reduce user confusion
- reduce unnecessary questions
- improve safe defaults
- improve memory safety
- improve observability traces
- add tests
- add plain-language examples
- turn real failed prompts into tests or benchmark scenarios

## Failed Prompt Loop

If AI failed to do everything, add the prompt to `skills/everything-ai/references/prompt-bank.md`.

Accepted prompts must land in at least one place:

- `tests/evals/everything_ai_benchmark.json`
- `skills/everything-ai/domains/*.md`

No accepted prompt stays prose-only.

## Pull Request Rules

- Explain the change in simple words.
- Include why the change helps non-technical users.
- For failed-prompt fixes, name the benchmark scenario or domain example you added.
- Do not add behavior that saves secrets or sensitive data.
- Do not save untrusted file, webpage, or tool output as user preference.
- Run tests before opening a PR:

```powershell
python .\tests\test_everything_ai.py
node .\scripts\install.js --dry-run
```

## Review Style

Reviews should be kind and direct. This project welcomes beginner contributors.
