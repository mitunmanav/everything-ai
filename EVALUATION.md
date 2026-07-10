# Evaluation

Latest local checks for v0.4.2:

- Test suite: 62/62 green
- Version: 0.4.2
- Key v0.4.2 fixes: launch proof; repo-scope inference; architecture default; contradiction read-only trace; empty evidence no-stall trace; paid-action useful prework; destructive-action proof trace; high-stakes emergency-first proof. If launch work is broad, it reports the assumption and first safe action. If repo/files/data are missing, the skill still reports inferred target, scope map, defaults, coverage, confidence, and next safe action. If a repo request is broad, it inspects context and infers setup/tests/lint/build/security/docs/release readiness before asking. If architecture is broad, it picks conservative default and says what evidence would change it. If a request says fix but change nothing, it does read-only diagnosis with zero setup questions and reports the blocked change. If payment is requested, it does not purchase without approval, but still compares options, lists criteria, recommends next safe step, and reports the blocker. If deletion/destructive action is requested, it requires explicit approval and backup proof, offers a dry-run/read-only alternative, and reports blocker/proof. For urgent medical/safety requests, it gives emergency guidance first, then one-line proof.
- Key v0.4.1 fix: removed `PLUGIN_DATA` branch from `context_inject.py`; hook reads from `EVERYTHING_AI_MEMORY_DIR` or `~/.agents/skills/everything-ai`.
- Regression guards: `test_empty_evidence_audit_still_reports_trace_and_next_action`, `test_paid_action_blocker_still_compares_and_reports_proof`, `test_high_stakes_response_keeps_emergency_first_and_one_line_proof`, `test_phase2_benchmark_proof_is_recorded_and_npm_test_stays_public`, and `test_phase_b_plugin_data_not_used_as_memory_dir`.
- Root cause evidence: `tests/results/v0.4.1-regression.json`
- Fix-confirmed chart: `tests/results/v0.4.1-fixed.svg`
- Live v0.4.2 targeted retest: gpt-5.5 medium/low ran through WSL for the targeted gaps. It captured live behavior proof, not a full benchmark score.
- Benchmark rule: keep the unbiased v0.4.0 full benchmark method unchanged. Targeted checks guide fixes only.
- Full Codex proof: v0.4.2 full Codex blind judge scored skill off 52.6%, skill on 96.1%, delta +43.5 points, with 40/40 raw outputs.

---

v0.4.0 live run (2026-06-19):

- gpt-5.5 · medium reasoning: off 88.2% → on 92.1%, delta **+3.9 pts**
- gpt-5.4-mini · low reasoning: off 75.0% → on 64.5%, delta **-10.5 pts** (PLUGIN_DATA bug — fixed in v0.4.1)
- Blind cross-model judge (Claude), n=20 per model
- Full data: `tests/results/v0.4.0-live-run.json`

v0.4.1 retest (2026-06-21, gpt-5.4-mini only):

- gpt-5.4-mini · low reasoning: off 88.2% → on 90.8%, delta **+2.6 pts** (fix confirmed, +13.1 pt recovery)
- n=40 · full data: `tests/results/v0.4.1-retest-run.json`

---

v0.3.0 checks (for history):

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
