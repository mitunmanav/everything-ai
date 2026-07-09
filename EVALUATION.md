# Evaluation

Latest status for v0.4.2:

- Unit tests: **44/44 passing**
- Live benchmark for v0.4.2: **not run yet**
- Honest status chart: `tests/results/v0.4.2-status.svg`
- Current public proof source: `TEST_RESULTS.md`

---

## Proven historical results

v0.4.0 live run (2026-06-19):

- gpt-5.5 · medium reasoning: off 88.2% → on 92.1%, **+3.9 pts**
- gpt-5.4-mini · low reasoning: off 75.0% → on 64.5%, **-10.5 pts**
- Judge: Claude (blind cross-model), n=20 per model
- Raw: `tests/results/v0.4.0-live-run.json`

v0.4.1 retest (2026-06-21, mini only):

- gpt-5.4-mini · low reasoning: off 88.2% → on 90.8%, **+2.6 pts**
- Recovery from bugged v0.4.0 mini run: **+13.1 pts swing**
- Raw: `tests/results/v0.4.1-retest-run.json`

---

## Known gaps (honest)

- v0.4.2 live benchmark run pending.
- No claim of new live-lift until fresh run exists.
- Public release quality depends on CI + package guard + version backup workflows.

---

## Automation status

On version update to `main` (`package.json` changed), GitHub now auto-runs:

- tests + public package guard
- release draft update
- backup tag + bundle artifact
- release tag + GitHub release creation
