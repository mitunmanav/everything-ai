#!/usr/bin/env python3
"""
Pre-push validation and release script for everything-ai.

Runs all checks, prints an honest preflight report, requires explicit
confirmation before pushing to main. Never lies. Never blocks on a missing
benchmark — but always says clearly what has and has not been run.

Usage:
    python3 scripts/push.py           # full preflight + push
    python3 scripts/push.py --dry-run # report only, no push
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today().isoformat()

PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"
INFO = "INFO"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(cmd, **kwargs):
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, **kwargs)


def _section(title):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print('─' * 60)


def _line(status, msg):
    icons = {PASS: "✓", WARN: "!", FAIL: "✗", INFO: "·"}
    print(f"  {icons[status]} [{status}] {msg}")


# ---------------------------------------------------------------------------
# Checks — each returns (status, message)
# ---------------------------------------------------------------------------

def check_unit_tests():
    result = subprocess.run(
        ["python3", "-m", "pytest", "tests/test_everything_ai.py", "-q", "--tb=no"],
        cwd=ROOT, capture_output=True, text=True,
    )
    lines = result.stdout.strip().splitlines()
    summary = lines[-1] if lines else "no output"
    if result.returncode == 0:
        return PASS, f"Unit tests: {summary}"
    return FAIL, f"Unit tests FAILED: {summary}"


def check_version_consistency():
    issues = []
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    version = package["version"]

    test_text = (ROOT / "tests" / "test_everything_ai.py").read_text(encoding="utf-8")
    # Only flag version strings that appear in package["version"] assertions — not historical
    # benchmark data checks (those reference old result JSON versions intentionally)
    stale_assertions = re.findall(
        r'package\["version"\]\s*==\s*"(\d+\.\d+\.\d+)"', test_text
    )
    stale = [v for v in stale_assertions if v != version]
    if stale:
        issues.append(f"package version assertions in tests still reference: {stale} (expected {version})")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if f"v{version}" not in readme:
        issues.append(f"README.md does not mention v{version}")

    tr = (ROOT / "TEST_RESULTS.md").read_text(encoding="utf-8")
    if f"v{version}" not in tr[:200]:
        issues.append(f"TEST_RESULTS.md header does not reference v{version}")

    badge_match = re.search(r'version-(\d+\.\d+\.\d+)-', readme)
    if badge_match and badge_match.group(1) != version:
        issues.append(f"Version badge shows {badge_match.group(1)}, package.json is {version}")

    if issues:
        return FAIL, "Version mismatch — " + "; ".join(issues)
    return PASS, f"Version consistent at {version} across package.json, README, tests, TEST_RESULTS"


def check_no_retest_pending():
    results_dir = ROOT / "tests" / "results"
    flagged = []
    for f in results_dir.glob("*.json"):
        if "retest-pending" in f.read_text(encoding="utf-8"):
            flagged.append(f.name)
    if flagged:
        return FAIL, f"retest-pending status in: {', '.join(flagged)} — resolve before pushing"
    return PASS, "No retest-pending flags in result files"


def check_benchmark_honesty():
    issues = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    tr = (ROOT / "TEST_RESULTS.md").read_text(encoding="utf-8")

    # Catch the specific misleading phrase we've had before
    if "gpt-5.5 baseline unchanged" in readme or "gpt-5.5 baseline unchanged" in tr:
        issues.append(
            "Found 'gpt-5.5 baseline unchanged' — misleading because gpt-5.5 was not re-run. "
            "Replace with explicit 'not re-run in vX.Y.Z, number is from vX.Y.Z run'."
        )

    # Catch projected numbers presented without a label
    if re.search(r"\+\d+ to \+\d+.*scope.defaults", tr):
        issues.append(
            "TEST_RESULTS appears to contain projected/estimated recovery numbers without "
            "clearly marking them as unconfirmed. Label or remove."
        )

    # Check that any version with an explicit "confirmed" live claim has a result JSON.
    # Only match phrases that assert a result was actually observed — not "pending" or "not run".
    confirmed_pattern = re.compile(
        r'v(\d+\.\d+\.\d+)[^\n]{0,80}live[^\n]{0,60}confirm',
        re.IGNORECASE,
    )
    for m in confirmed_pattern.finditer(readme + tr):
        v = m.group(1)
        jsons = list((ROOT / "tests" / "results").glob(f"v{v}*.json"))
        if not jsons:
            issues.append(
                f"README/TEST_RESULTS has 'live...confirmed' claim for v{v} but no result JSON found"
            )

    if issues:
        return FAIL, "Honesty issues — " + "; ".join(issues)
    return PASS, "No misleading benchmark claims detected"


def check_live_benchmark_status():
    """Informational only — reports what has and hasn't been run. Never blocks push."""
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    version = package["version"]
    results_dir = ROOT / "tests" / "results"

    current_jsons = list(results_dir.glob(f"v{version}*.json"))
    all_jsons = sorted(results_dir.glob("v*.json"))
    last_run = all_jsons[-1].name if all_jsons else "none"

    if current_jsons:
        return INFO, f"Live benchmark: results exist for v{version} ({', '.join(f.name for f in current_jsons)})"
    return WARN, (
        f"Live benchmark: NOT RUN for v{version}. "
        f"Last run: {last_run}. "
        f"Push will proceed but results section will show this gap."
    )


def check_svg_exists():
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    version = package["version"]
    svgs = list((ROOT / "tests" / "results").glob(f"v{version}*.svg"))
    if svgs:
        return INFO, f"SVG proof found for v{version}: {', '.join(f.name for f in svgs)}"
    return WARN, f"No SVG proof for v{version} — README chart will reference older version's SVG"


def check_no_placeholder_text():
    issues = []
    files_to_check = [
        ROOT / "README.md",
        ROOT / "TEST_RESULTS.md",
    ]
    bad_phrases = ["TODO", "FIXME", "TBD", "placeholder", "coming soon", "fill in"]
    for path in files_to_check:
        text = path.read_text(encoding="utf-8")
        for phrase in bad_phrases:
            if phrase.lower() in text.lower():
                issues.append(f"{path.name} contains '{phrase}'")
    if issues:
        return WARN, "Placeholder text found — " + "; ".join(issues)
    return PASS, "No placeholder text found in README or TEST_RESULTS"


def check_git_state():
    status = _run(["git", "status", "--porcelain"])
    uncommitted = [l for l in status.stdout.splitlines() if l.strip()]
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    if uncommitted:
        return WARN, f"Uncommitted changes ({len(uncommitted)} files) on branch '{branch}' — will be committed"
    return INFO, f"Working tree clean on branch '{branch}'"


def check_unit_test_count_in_badge():
    """Ensure the unit test badge count matches actual collected tests."""
    result = subprocess.run(
        ["python3", "-m", "pytest", "tests/test_everything_ai.py", "--collect-only", "-q"],
        cwd=ROOT, capture_output=True, text=True,
    )
    lines = result.stdout.strip().splitlines()
    # Last line is something like "46 tests collected in 0.18s"
    match = re.search(r"(\d+) test", lines[-1] if lines else "")
    if not match:
        return WARN, "Could not determine test count from pytest --collect-only"
    actual = match.group(1)

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    badge_match = re.search(r"unit%20tests-(\d+)%2F(\d+)", readme)
    if not badge_match:
        return WARN, "Unit test badge not found in README"
    badge_count = badge_match.group(2)
    if badge_count != actual:
        return FAIL, f"Unit test badge says {badge_count} tests but pytest collects {actual} — update README badge"
    return PASS, f"Unit test badge count matches: {actual} tests"


# ---------------------------------------------------------------------------
# Report + push
# ---------------------------------------------------------------------------

def run_preflight():
    _section("PREFLIGHT REPORT")
    print(f"  Date: {TODAY}")
    print(f"  Repo: {ROOT.name}")

    checks = [
        check_unit_tests,
        check_version_consistency,
        check_unit_test_count_in_badge,
        check_no_retest_pending,
        check_benchmark_honesty,
        check_live_benchmark_status,
        check_svg_exists,
        check_no_placeholder_text,
        check_git_state,
    ]

    results = []
    for fn in checks:
        status, msg = fn()
        _line(status, msg)
        results.append((status, msg))

    failures = [r for r in results if r[0] == FAIL]
    warnings = [r for r in results if r[0] == WARN]

    _section("SUMMARY")
    print(f"  Failures : {len(failures)}")
    print(f"  Warnings : {len(warnings)}")
    print()
    if failures:
        print("  PUSH BLOCKED. Fix failures before pushing:")
        for _, msg in failures:
            print(f"    ✗ {msg}")
        return False
    if warnings:
        print("  Warnings present (push allowed — documented above).")
    else:
        print("  All checks passed.")
    return True


def show_git_diff_summary():
    _section("CHANGES TO BE PUSHED")
    log = _run(["git", "log", "origin/main..HEAD", "--oneline"])
    if log.stdout.strip():
        print("  Commits ahead of origin/main:")
        for line in log.stdout.strip().splitlines():
            print(f"    {line}")
    else:
        status = _run(["git", "status", "--porcelain"])
        uncommitted = status.stdout.strip().splitlines()
        if uncommitted:
            print("  Uncommitted files to be committed first:")
            for line in uncommitted:
                print(f"    {line}")
        else:
            print("  Nothing to push — already up to date.")


def commit_uncommitted(version):
    status = _run(["git", "status", "--porcelain"])
    if not status.stdout.strip():
        return
    _section("COMMITTING UNCOMMITTED CHANGES")
    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"chore: pre-push cleanup for v{version}"],
        cwd=ROOT, check=True,
    )
    print("  Committed.")


def push_to_main():
    _section("PUSHING TO MAIN")
    result = subprocess.run(
        ["git", "push", "origin", "HEAD:main"],
        cwd=ROOT,
    )
    if result.returncode == 0:
        print("  Pushed to main.")
    else:
        print("  Push failed. Check git output above.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Pre-push validation for everything-ai")
    parser.add_argument("--dry-run", action="store_true", help="Report only, do not push")
    args = parser.parse_args()

    ok = run_preflight()
    if not ok:
        sys.exit(1)

    show_git_diff_summary()

    if args.dry_run:
        print("\n  --dry-run: stopping here. No changes pushed.")
        return

    _section("CONFIRMATION")
    print("  Review the report above.")
    print("  Type 'yes' to commit any uncommitted changes and push to main.")
    print("  Anything else aborts.")
    answer = input("  > ").strip().lower()
    if answer != "yes":
        print("  Aborted.")
        sys.exit(0)

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    commit_uncommitted(package["version"])
    push_to_main()


if __name__ == "__main__":
    main()
