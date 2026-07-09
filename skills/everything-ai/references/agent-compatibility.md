# Agent Compatibility Brief

Sources checked:
- Claude Code skills: https://code.claude.com/docs/en/skills
- Claude Agent SDK skills: https://code.claude.com/docs/en/agent-sdk/skills
- Claude skill best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Codex skills: https://developers.openai.com/codex/skills/create-skill

Rules for Everything AI:
- Keep `SKILL.md` portable: YAML `name` + `description`, then Markdown instructions.
- Front-load trigger words in `description`; both Codex and Claude use it for discovery.
- Keep `SKILL.md` concise. Put heavy details in one-level `references/` files.
- Use forward-slash paths, even on Windows.
- Do not rely on Claude-only dynamic context injection or tool frontmatter for core behavior.
- Do not add user-facing process modes. Everything AI means AI carries the checklist.
- Test prompt behavior for both direct invocation (`$everything-ai`, `/everything-ai`) and implicit "do everything" requests.
