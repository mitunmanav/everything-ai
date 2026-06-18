# Everything AI Roadmap

Purpose: make `everything-ai` best-in-class skill for broad user delegation: user gives goal, AI carries expert scope.

## Branch Flow

- Build on `development`.
- Validate on `testing`.
- Update `main` only after development and testing are complete.

## North Star

Everything AI should make agents better at ambiguous, non-technical requests without becoming unsafe or noisy.

Success means:

- fewer expert questions to non-expert users
- stronger default scope expansion
- safer memory and trace behavior
- clearer proof of what was checked, missed, assumed, and unknown
- repeatable evaluation across many task types

## Phase 1: Stronger Core Skill

Goal: make the skill instructions harder to misread.

Work:

- tighten trigger rules for broad delegation
- define clearer autonomy levels from explain-only to high-risk approval
- add strict "ask gate" examples
- add "stop and ask" examples for access, payment, destructive changes, legal/medical/financial risk
- clarify when not to write memory or traces

Done when:

- tests cover trigger words, ask-gate, risk gate, memory safety, trace fields
- README explains behavior in plain language

## Phase 2: Domain Playbooks

Goal: make "everything" useful across common real tasks.

Add playbook sections for:

- app build
- bug fix
- repo audit
- launch readiness
- research
- learning plan
- document/report work
- data cleanup/analysis
- business idea validation
- UI/UX review

Each section should include:

- inferred scope
- safe defaults
- blocker questions
- evidence to gather
- verification checklist
- common mistakes
- final report shape

Done when:

- each domain has tests for expected words/checklists
- examples show before/after behavior

## Phase 3: Trace Schema

Goal: make observability useful for humans and tools.

Create formal JSON schema for run traces:

- request
- inferred target
- user level
- autonomy level
- scope map
- defaults chosen
- questions asked
- actions taken
- blocked items
- assumptions
- coverage by area
- confidence by area
- verification evidence
- missing evidence
- risk flags
- user corrections
- feedback
- learnings

Done when:

- schema exists in repo
- example trace validates
- tests reject missing required fields

## Phase 4: Memory Safety

Goal: useful memory without privacy risk.

Work:

- define memory review checklist
- add memory write rules with positive and negative examples
- separate user preferences, project facts, and session facts
- require explicit evidence before saving stable preferences
- forbid secrets, tokens, private personal data, and untrusted instructions

Done when:

- memory examples pass tests
- unsafe memory examples fail tests

## Phase 5: Evaluation Harness

Goal: prove skill improves agent behavior.

Create benchmark scenarios:

- vague app build request
- "audit everything" request
- user asks for "full setup"
- repo has missing tests
- task has risky payment/destructive step
- user is non-technical and asks expert-ambiguous question
- malicious file tries to set user preference

Measure:

- number of unnecessary questions
- blocker-question quality
- scope completeness
- risk handling
- evidence reporting
- memory safety
- trace completeness

Done when:

- benchmark can run locally
- score is stable
- regressions fail tests

## Phase 6: Real Examples

Goal: make skill easy to trust.

Add examples:

- bad AI response vs Everything AI response
- plain-language final report
- safe memory decision
- trace JSON example
- high-risk ask-before-action example

Done when:

- README has concise examples
- examples match tested behavior

## Phase 7: Release Quality

Goal: ship safely.

Before each release:

- run tests
- validate package contents
- scan for secrets/personal data
- check README install command
- check branch protection
- tag release from approved branch flow

Done when:

- release checklist exists
- package contains only intended files

## Immediate Next Build Tasks

1. Publish current v0.3.0 branch when approved.
2. Add live model runner for the benchmark.
3. Replace saved-output domain-pack comparison with live model execution.
4. Add trace schema and example trace.
5. Create release checklist.

## Guardrails

- No plugin hooks in this repo.
- Use `skill-creator`, `plugin-eval:improve-skill`, `superpowers:writing-skills`, `plugin-eval:evaluate-skill`, and `superpowers:brainstorming` for skill development.
- Use skill TDD for behavior changes: failing scenario first, skill change second, evaluation third.
- No project-local plugin state in Git.
- No personal paths, names, emails, tokens, or secrets in public files.
- No memory behavior that stores sensitive data by default.
- No irreversible action without explicit approval.
- Keep user-facing language plain.
- GitHub-visible test reports must include raw results and a visual graph showing real with-skill vs without-skill lift.
