# Coding

## Scope Defaults
Treat code, bug, build, refactor, review, and deploy requests as move-from-problem-to-working-software. Start with reading existing code before writing any. On bugs: diagnosis first, read-only. On new features: smallest working increment. On refactors: behavior-preserving changes only. On deploys: dry-run first. Exclude architecture redesigns, team process changes, or infrastructure cost decisions unless explicitly approved.

Default scope includes: reading the error or goal, mapping affected files, identifying root cause or feature gap, implementing the minimal fix, running available tests, checking for side effects, and reporting what changed and why.

## Checklist
- Read the full error message or feature request before touching any file.
- Identify which files are involved. Read them before editing.
- On bugs: state the root cause in one sentence before proposing a fix.
- Write or update a test that fails before the fix and passes after.
- Implement the minimal change that makes the test pass.
- Run all available tests. Report pass/fail counts.
- Check for side effects: search for other callers of changed functions.
- Report: what was changed, why, what tests pass, what is untested, what assumptions were made.

## Pitfalls
- Editing files before reading them.
- Fixing symptoms instead of root causes.
- Adding abstraction for a problem that only appears once.
- Skipping test verification after a fix.
- Assuming environment setup (dependencies, env vars) without checking.
- Refactoring while fixing — do one or the other per commit.

## Success Looks Like
The bug is fixed or the feature works. A test proves it. No existing tests broke. The change is small and focused. The report names what was changed, what was tested, what assumptions were made, and what still needs human review (security, performance, edge cases).

## Examples
Example 1: "Fix my bug." Read the error message and stack trace. Identify the file and line. State root cause in one sentence. Write a failing test. Fix. Run tests. Report: fixed X in Y, test added, N tests pass.

Example 2: "Build a login feature." Read the existing auth code first. Pick the simplest working approach (session token vs JWT based on what already exists). Implement in one file. Add tests. Report what was built, what was skipped (OAuth, 2FA), and what to review before shipping.
