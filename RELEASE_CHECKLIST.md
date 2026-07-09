# Everything AI Release Checklist

Release goal: ship the "AI do everything" skill without local leaks, fake proof, or agent-specific breakage.

## Required Checks

- Run `npm.cmd test`.
- Run `python "%USERPROFILE%\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "skills/everything-ai"`.
- Run `npm.cmd pack --dry-run` and inspect included files.
- Verify Codex install dry run through `node scripts/install.js --dry-run --agent openai`.
- Verify Claude install dry run through `node scripts/install.js --dry-run --agent claude`.
- Confirm `skills/everything-ai/references/trace.schema.json` and `skills/everything-ai/references/example-trace.json` are included.
- Confirm `skills/everything-ai/references/agent-compatibility.md` reflects current Codex and Claude docs.
- Confirm no local-only files ship. No `AGENTS.md`, `.codex/`, `.claude/`, `.superpowers/`, secrets, tokens, emails, or machine paths.
- Confirm README proof numbers match the latest verified local run.

## Approval Gate

Do not publish, tag, push release branches, or upload packages without explicit approval.

## Release Notes Shape

- What changed.
- Why it helps people who want AI to do everything.
- What was verified.
- What remains unverified or blocked.
