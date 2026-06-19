#!/usr/bin/env python3
"""Rerun the runs that failed transiently during a live benchmark batch.

Failures in the batch are almost always transient (an API/network blip while
many codex processes run at once), not bad prompts. This script reads the run
log, finds the FAILED/TIMEOUT runs, rebuilds the exact same prompt for each,
reruns it, and patches the raw output plus arm_key.json / judge_input.json so
the dataset is complete. It records what it did to a rerun_report.json.

Usage:
  python3 scripts/rerun_failures.py --out v0.4.0-live-mini --model gpt-5.4-mini --reasoning low
"""
import argparse
import json
import re
import tempfile
from pathlib import Path

from run_live_benchmark import (
    ROOT, BENCHMARK, SKILL, normalize, build_prompt, run_one,
)

LOG_LINE = re.compile(r"\[(\d+)/\d+\]\s+(run_\d+)\s+(\S+)\s+(skill_on|skill_off)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output subdir under tests/results")
    ap.add_argument("--model", required=True)
    ap.add_argument("--reasoning", default=None)
    ap.add_argument("--log", required=True, help="path to the batch run log")
    args = ap.parse_args()

    out_dir = ROOT / "tests" / "results" / args.out
    raw_dir = out_dir / "raw"
    log_lines = Path(args.log).read_text(encoding="utf-8").splitlines()

    # A run failed if its dispatch line is immediately followed by FAILED/TIMEOUT.
    failed = []
    for i, line in enumerate(log_lines):
        m = LOG_LINE.search(line)
        if not m:
            continue
        nxt = log_lines[i + 1] if i + 1 < len(log_lines) else ""
        if "FAILED" in nxt or "TIMEOUT" in nxt:
            failed.append({"run_id": m.group(2), "scenario_id": m.group(3), "arm": m.group(4)})

    if not failed:
        print("No failed runs found. Nothing to rerun.")
        return

    benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    skill_text = SKILL.read_text(encoding="utf-8")
    by_id = {s["id"]: s for s in benchmark["scenarios"]}

    arm_key = json.loads((out_dir / "arm_key.json").read_text(encoding="utf-8"))
    judge_input = json.loads((out_dir / "judge_input.json").read_text(encoding="utf-8"))
    have = {e["run_id"] for e in judge_input}
    neutral_dir = Path(tempfile.mkdtemp(prefix="eai-rerun-"))

    report = []
    for f in failed:
        run_id, sid, arm = f["run_id"], f["scenario_id"], f["arm"]
        if run_id in have:
            report.append({**f, "result": "already_present_skipped"})
            continue
        norm = normalize(by_id[sid])
        prompt = build_prompt(norm, skill_text, arm == "skill_on")
        out_file = raw_dir / f"{run_id}.txt"
        print(f"rerun {run_id} {sid} {arm} ...", flush=True)
        try:
            ok = run_one(prompt, out_file, neutral_dir, args.model, args.reasoning)
        except Exception as e:  # noqa: BLE001
            ok = False
            print(f"  rerun error: {e}", flush=True)
        if not ok:
            report.append({**f, "result": "rerun_failed_again"})
            print("  STILL FAILED", flush=True)
            continue
        arm_key[run_id] = {"scenario_id": sid, "arm": arm}
        judge_input.append({
            "run_id": run_id,
            "scenario_id": sid,
            "domain": norm["domain"],
            "user_prompt": norm["prompt_text"],
            "context": norm["context"],
            "reference": norm["reference"],
            "fail_traps": norm["fail_traps"],
            "required_metrics": norm["required_metrics"],
            "hard_fail_metrics": norm["hard_fail_metrics"],
            "output_file": f"raw/{run_id}.txt",
        })
        report.append({**f, "result": "rerun_succeeded"})
        print("  OK", flush=True)

    # keep judge_input in run order
    judge_input.sort(key=lambda e: e["run_id"])
    (out_dir / "arm_key.json").write_text(json.dumps(arm_key, indent=2), encoding="utf-8")
    (out_dir / "judge_input.json").write_text(json.dumps(judge_input, indent=2), encoding="utf-8")
    (out_dir / "rerun_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    ok_n = sum(1 for r in report if r["result"] == "rerun_succeeded")
    print(f"\nReran {len(failed)} failed run(s): {ok_n} recovered. See {out_dir}/rerun_report.json")


if __name__ == "__main__":
    main()
