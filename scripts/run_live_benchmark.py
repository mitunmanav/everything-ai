#!/usr/bin/env python3
"""Live v0.4.0 benchmark runner.

Runs the model-under-test (gpt-5.5 via `codex exec`) against every scenario in
the benchmark twice: skill OFF (bare prompt) and skill ON (SKILL.md prepended).
All raw outputs are saved with anonymized run IDs so a separate blind judge can
score them without knowing which arm produced which output.

Honesty design:
- Every raw output is written to disk and committed (auditable).
- run_XXX IDs are shuffled; the arm mapping lives in arm_key.json, which the
  judge never reads.
- judge_input.json carries only prompt + output + rubric per run, no arm.

Usage:
  python3 scripts/run_live_benchmark.py            # all 20 scenarios, both arms
  python3 scripts/run_live_benchmark.py --limit 1  # smoke: first scenario only
"""
import argparse
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "tests" / "evals" / "everything_ai_benchmark.json"
SKILL = ROOT / "skills" / "everything-ai" / "SKILL.md"
DEFAULT_MODEL = "gpt-5.5"
RUN_TIMEOUT = 240  # seconds per model call


def normalize(scenario):
    """The benchmark holds two scenario schemas. Original 10 carry user_prompt +
    a rich rubric (expected_behavior, fail_traps, required_metrics). The 10 added
    in v0.4.0 carry prompt + saved_output (an ideal trace). Normalize both to one
    shape so every scenario runs and is judged on the same footing."""
    prompt_text = scenario.get("user_prompt") or scenario.get("prompt") or ""
    context = scenario.get("context", "")
    if "expected_behavior" in scenario:
        reference = {"expected_behavior": scenario["expected_behavior"]}
    elif "saved_output" in scenario:
        reference = {"ideal_trace": scenario["saved_output"]}
    else:
        reference = {}
    return {
        "id": scenario["id"],
        "domain": scenario.get("domain", ""),
        "prompt_text": prompt_text,
        "context": context,
        "reference": reference,
        "fail_traps": scenario.get("fail_traps", []),
        "required_metrics": scenario.get("required_metrics", []),
        "hard_fail_metrics": scenario.get("hard_fail_metrics", []),
    }


def build_prompt(norm, skill_text, skill_on):
    request = norm["prompt_text"]
    if norm["context"]:
        request += f"\n\nContext: {norm['context']}"
    if not skill_on:
        return request
    return (
        f"{skill_text}\n\n"
        "----- end of skill -----\n\n"
        "Handle the following request using the skill above.\n\n"
        f"{request}"
    )


def run_one(prompt, out_file, work_dir, model, reasoning=None):
    """Run codex exec headless in a neutral dir, write final message to out_file.

    The neutral working directory matters: running inside a real code repo biases
    the bare agent toward auditing that repo instead of answering the user. A real
    non-technical user is not sitting in this repo, so both arms run in an empty
    scratch dir to isolate the skill's effect.
    """
    cmd = [
        "codex", "exec", "-",
        "-m", model,
        "-s", "read-only",
        "--ephemeral",
        "--skip-git-repo-check",
        "-o", str(out_file),
    ]
    if reasoning:
        cmd[3:3] = ["-c", f"model_reasoning_effort={reasoning}"]
    result = subprocess.run(
        cmd,
        input=prompt,
        text=True,
        capture_output=True,
        timeout=RUN_TIMEOUT,
        cwd=str(work_dir),
    )
    return result.returncode == 0 and out_file.exists() and out_file.read_text(encoding="utf-8").strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="run only first N scenarios")
    parser.add_argument("--seed", type=int, default=42, help="shuffle seed for run IDs")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="model under test")
    parser.add_argument("--reasoning", default=None, help="model_reasoning_effort override (e.g. low)")
    parser.add_argument("--out", default="v0.4.0-live", help="output subdir under tests/results")
    args = parser.parse_args()

    model = args.model
    out_dir = ROOT / "tests" / "results" / args.out
    raw_dir = out_dir / "raw"

    benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    skill_text = SKILL.read_text(encoding="utf-8")
    scenarios = benchmark["scenarios"]
    if args.limit:
        scenarios = scenarios[: args.limit]

    raw_dir.mkdir(parents=True, exist_ok=True)
    neutral_dir = Path(tempfile.mkdtemp(prefix="eai-live-"))

    # Build the full job list (scenario x arm), then shuffle run IDs.
    jobs = []
    for scenario in scenarios:
        norm = normalize(scenario)
        for skill_on in (False, True):
            jobs.append((norm, skill_on))
    rng = random.Random(args.seed)
    rng.shuffle(jobs)

    arm_key = {}
    judge_input = []
    failures = []

    for idx, (norm, skill_on) in enumerate(jobs, start=1):
        run_id = f"run_{idx:03d}"
        out_file = raw_dir / f"{run_id}.txt"
        prompt = build_prompt(norm, skill_text, skill_on)
        arm = "skill_on" if skill_on else "skill_off"
        print(f"[{idx}/{len(jobs)}] {run_id} {norm['id']} {arm} ...", flush=True)
        try:
            ok = run_one(prompt, out_file, neutral_dir, model, args.reasoning)
        except subprocess.TimeoutExpired:
            ok = False
            print(f"  TIMEOUT", flush=True)
        if not ok:
            failures.append(run_id)
            print(f"  FAILED", flush=True)
            continue

        arm_key[run_id] = {"scenario_id": norm["id"], "arm": arm}
        judge_input.append({
            "run_id": run_id,
            "scenario_id": norm["id"],
            "domain": norm["domain"],
            "user_prompt": norm["prompt_text"],
            "context": norm["context"],
            "reference": norm["reference"],
            "fail_traps": norm["fail_traps"],
            "required_metrics": norm["required_metrics"],
            "hard_fail_metrics": norm["hard_fail_metrics"],
            "output_file": f"raw/{run_id}.txt",
        })

    (out_dir / "arm_key.json").write_text(json.dumps(arm_key, indent=2), encoding="utf-8")
    (out_dir / "judge_input.json").write_text(json.dumps(judge_input, indent=2), encoding="utf-8")

    print(f"\nDone. {len(judge_input)} ok, {len(failures)} failed.", flush=True)
    if failures:
        print("failed run ids:", ", ".join(failures), flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
