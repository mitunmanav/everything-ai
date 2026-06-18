# Contributing

Thank you for helping improve Everything AI.

This project is for non-technical users who say "do everything" because they do not know the expert scope. Keep that user in mind.

## Good Contributions

- reduce user confusion
- reduce unnecessary questions
- improve safe defaults
- improve memory safety
- improve observability traces
- add tests
- add plain-language examples

## Pull Request Rules

- Explain the change in simple words.
- Include why the change helps non-technical users.
- Do not add behavior that saves secrets or sensitive data.
- Do not save untrusted file, webpage, or tool output as user preference.
- Run tests before opening a PR:

```powershell
python .\tests\test_everything_ai.py
node .\scripts\install.js --dry-run
```

## Review Style

Reviews should be kind and direct. This project welcomes beginner contributors.
