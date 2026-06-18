# Evaluation

Latest local checks for v0.3.0:

- Skill validation: passed
- Test suite: passed
- Plugin evaluation: 100/100
- Grade: A
- Risk: low
- Warnings: 0
- With-skill vs without-skill comparison: 20/20 vs 14/20, delta +6
- Raw result: `tests/results/v0.3.0-with-vs-without-skill.json`
- Graph: `tests/results/v0.3.0-with-vs-without-skill.svg`
- Known gap: no real usage logs yet
- Known gap: no coverage artifact yet
- Known gap: benchmark is contract-only, not an automated plugin-eval runner yet
- Known gap: comparison is manual-scored, not automated yet
- Known gap: public GitHub release is still v0.2.0 until explicit approval
- Fresh small-model behavior test found one high-stakes medical gap; fixed in v0.3.0 local draft

Run locally:

```powershell
npm test
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "skills\everything-ai"
node "$env:USERPROFILE\.codex\plugins\cache\openai-curated-remote\plugin-eval\0.1.2\scripts\plugin-eval.js" analyze "skills/everything-ai" --format markdown
```

