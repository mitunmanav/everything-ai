#!/usr/bin/env python3
"""Smart push script for everything-ai. Detects what changed and runs contextual checks.
Run with: python3 scripts/push.py
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, **kwargs):
    return subprocess.run(cmd, cwd=ROOT, check=True, text=True, capture_output=True, **kwargs)


def get_changed_files():
    unstaged = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=ROOT, text=True, capture_output=True,
    )
    staged = subprocess.run(
        ["git", "diff", "--name-only", "--cached"],
        cwd=ROOT, text=True, capture_output=True,
    )
    return set(
        unstaged.stdout.splitlines() + staged.stdout.splitlines()
    )


def get_version():
    return json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]


def run_tests():
    print("Running full test suite...")
    result = subprocess.run(
        ["pytest", "tests/test_everything_ai.py", "-v"],
        cwd=ROOT,
    )
    if result.returncode != 0:
        print("Tests failed. Aborting push.")
        sys.exit(1)
    print("All tests passed.")


def check_no_retest_pending():
    results_dir = ROOT / "tests" / "results"
    for f in results_dir.glob("*.json"):
        if "retest-pending" in f.read_text(encoding="utf-8"):
            print(f"ERROR: {f.name} still contains retest-pending status. Fix before pushing.")
            sys.exit(1)


def check_svg_and_docs_updated(version):
    svgs = list((ROOT / "tests" / "results").glob(f"v{version}*.svg"))
    if not svgs:
        print(f"ERROR: No SVG found for v{version} in tests/results/. Generate it first.")
        sys.exit(1)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if f"v{version}" not in readme:
        print(f"ERROR: README.md not updated for v{version}.")
        sys.exit(1)
    test_results = (ROOT / "TEST_RESULTS.md").read_text(encoding="utf-8")
    if f"v{version}" not in test_results:
        print(f"ERROR: TEST_RESULTS.md not updated for v{version}.")
        sys.exit(1)
    print(f"SVG and docs verified for v{version}.")


def commit_if_dirty(version):
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT, text=True, capture_output=True,
    )
    if status.stdout.strip():
        subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"chore: release v{version}"],
            cwd=ROOT, check=True,
        )
        print(f"Committed changes for v{version}.")


def tag_and_release(version):
    existing = subprocess.run(
        ["git", "tag", "--list", f"v{version}"],
        cwd=ROOT, text=True, capture_output=True,
    )
    if existing.stdout.strip():
        print(f"Tag v{version} already exists. Skipping release.")
        return
    check_svg_and_docs_updated(version)
    subprocess.run(["git", "tag", f"v{version}"], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", f"v{version}"], cwd=ROOT, check=True)
    subprocess.run(
        ["gh", "release", "create", f"v{version}", "--generate-notes"],
        cwd=ROOT, check=True,
    )
    print(f"GitHub release v{version} created.")


def main():
    changed = get_changed_files()
    version = get_version()

    # Always: run full test suite
    run_tests()

    # Contextual checks
    if any(f.startswith("tests/results/") and f.endswith(".json") for f in changed):
        check_no_retest_pending()

    # Commit uncommitted changes
    commit_if_dirty(version)

    # Push to main
    subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)
    print("Pushed to main.")

    # Version-bump path: tag + release if no tag exists for current version
    tag_and_release(version)


if __name__ == "__main__":
    main()
