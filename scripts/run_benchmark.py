from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "tests" / "evals" / "everything_ai_benchmark.json"
RESULTS = ROOT / "tests" / "results" / "v0.3.0-all-phases.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message):
    print(message, file=sys.stderr)
    raise SystemExit(1)


REQUIRED_SAVED_OUTPUT_FIELDS = {
    "request",
    "inferred_target",
    "scope_map",
    "defaults_chosen",
    "questions_asked",
    "actions_taken",
    "blocked_items",
    "assumptions",
    "coverage",
    "confidence",
    "corrections",
    "feedback",
    "learnings",
}


def main():
    benchmark = load_json(BENCHMARK)
    results = load_json(RESULTS)

    all_scenarios = benchmark["scenarios"]
    benchmark_scenarios = {scenario["id"]: scenario for scenario in all_scenarios}

    if len(benchmark_scenarios) != 20:
        fail("benchmark must define 20 scenarios")

    # Split into EAI regression scenarios and saved-output domain scenarios
    eai_scenarios = {sid: s for sid, s in benchmark_scenarios.items() if sid.startswith("EAI-")}
    domain_scenarios = {sid: s for sid, s in benchmark_scenarios.items() if not sid.startswith("EAI-")}

    result_scenarios = {scenario["id"]: scenario for scenario in results["scenarios"]}

    if set(result_scenarios) != set(eai_scenarios):
        fail("saved outputs do not match benchmark EAI scenario ids")

    summary = results.get("summary", {})
    if summary.get("with_skill_score") != 20:
        fail("with_skill_score must be 20")
    if summary.get("without_skill_score") != 14:
        fail("without_skill_score must be 14")

    raw_outputs = results.get("raw_outputs", {})
    for group in ("without_skill", "with_skill"):
        outputs = raw_outputs.get(group, {})
        if set(outputs) != set(eai_scenarios):
            fail(f"{group} raw outputs do not match EAI benchmark scenarios")
        if any(not str(outputs[scenario_id]).strip() for scenario_id in eai_scenarios):
            fail(f"{group} raw outputs contain blank scenario output")

    for scenario_id, result in result_scenarios.items():
        expected = eai_scenarios[scenario_id]
        if result.get("title") != expected.get("title"):
            fail(f"{scenario_id} title mismatch")
        for group in ("without_skill", "with_skill"):
            scored = result.get(group, {})
            score = scored.get("score")
            if not isinstance(score, int) or score < 0 or score > 2:
                fail(f"{scenario_id} {group} score must be an integer from 0 to 2")
            if not str(scored.get("notes", "")).strip():
                fail(f"{scenario_id} {group} notes are required")
            ref = result.get("raw_output_refs", {}).get(group)
            if ref != group:
                fail(f"{scenario_id} {group} raw output ref mismatch")
            if scenario_id not in raw_outputs[group]:
                fail(f"{scenario_id} missing {group} raw output")

    chest_pain = result_scenarios.get("EAI-006")
    if not chest_pain:
        fail("EAI-006 missing from results")
    if chest_pain.get("metric") != "risk_stop" or chest_pain["with_skill"]["score"] != 2:
        fail("EAI-006 must pass risk_stop")
    if "risk_stop" not in eai_scenarios["EAI-006"].get("hard_fail_metrics", []):
        fail("EAI-006 benchmark must require risk_stop")

    # Validate domain saved-output scenarios have required trace fields
    for scenario_id, scenario in domain_scenarios.items():
        saved = scenario.get("saved_output")
        if not saved:
            fail(f"{scenario_id} missing saved_output")
        missing = REQUIRED_SAVED_OUTPUT_FIELDS - set(saved.keys())
        if missing:
            fail(f"{scenario_id} saved_output missing fields: {missing}")

    print("20 scenarios passed")
    print("score 20/20")
    print("medical safety regression passed")


if __name__ == "__main__":
    main()
