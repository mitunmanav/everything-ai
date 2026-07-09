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
npm test
```

- For maintainer repo-hardening setup (labels/settings), run:

```powershell
.\scripts\bootstrap-github.ps1 -Owner mitunmanav -Repo everything-ai
```

- For version backup + rollback safety:

```powershell
git fetch origin --tags
git tag --list "backup-v*"
.\scripts\rollback-from-backup.ps1 -BackupTag "<backup-tag>"
```

## Review Style

Reviews should be kind and direct. This project welcomes beginner contributors.
