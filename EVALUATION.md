# Evaluation

Latest local checks for v0.3.0:

- Skill validation: passed
- Test suite: passed
- Plugin evaluation: 100/100
- Grade: A
- Risk: low
- Warnings: 0
- With-skill vs without-skill comparison: 20/20 vs 14/20, delta +6
- Domain-pack comparison: 24/24 vs 18/24, delta +6
- Runnable benchmark regression suite: passed
- Claude metadata: present
- GitHub Actions workflow: present
- Domain packs: startup, data analysis, personal productivity
- Visible-output token estimate: with skill 295, without skill 210, delta +85
- Plugin-eval static skill budget: trigger 39, invoke 372, deferred 516, total 927 tokens
- Raw result: `tests/results/v0.3.0-with-vs-without-skill.json`
- Graph: `tests/results/v0.3.0-with-vs-without-skill.svg`
- Known gap: no real usage logs yet
- Known gap: no coverage artifact yet
- Known gap: benchmark is saved-output based, not a live model runner yet
- Known gap: comparison is manual-scored, not automated yet
- Known gap: domain-specific lift is saved-output based, not live model execution yet
- Known gap: public GitHub release is still v0.2.0 until explicit approval
- Fresh small-model behavior test found one high-stakes medical gap; fixed in v0.3.0 local draft

Run locally:

```powershell
npm test
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "skills\everything-ai"
node "$env:USERPROFILE\.codex\plugins\cache\openai-curated-remote\plugin-eval\0.1.2\scripts\plugin-eval.js" analyze "skills/everything-ai" --format markdown
```

