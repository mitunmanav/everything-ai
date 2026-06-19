from pathlib import Path
import json
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "everything-ai" / "SKILL.md"
PLAYBOOK = ROOT / "skills" / "everything-ai" / "references" / "playbook.md"
BENCHMARK = ROOT / "tests" / "evals" / "everything_ai_benchmark.json"
PACKAGE = ROOT / "package.json"
ROADMAP = ROOT / "ROADMAP.md"
TEST_RESULTS = ROOT / "TEST_RESULTS.md"
README = ROOT / "README.md"
CLAUDE_AGENT = ROOT / "skills" / "everything-ai" / "agents" / "claude.yaml"
BENCHMARK_RUNNER = ROOT / "scripts" / "run_benchmark.py"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "test.yml"
COMPARISON_RESULT = ROOT / "tests" / "results" / "v0.3.0-all-phases.json"
COMPARISON_GRAPH = ROOT / "tests" / "results" / "v0.3.0-all-phases.svg"
DOMAINS = ROOT / "skills" / "everything-ai" / "domains"
AGENTS = ROOT / "skills" / "everything-ai" / "agents"
PUBLIC_FILES = [
    README,
    ROOT / "ROADMAP.md",
    ROOT / "EVALUATION.md",
    ROOT / "TEST_RESULTS.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "SECURITY.md",
    ROOT / "CODE_OF_CONDUCT.md",
    SKILL,
    PLAYBOOK,
]
RELEASE_EXCLUDED_FILES = [ROOT / "AGENTS.md"]

REQUIRED_METRICS = {
    "ask_gate",
    "scope_inference",
    "safe_defaults",
    "risk_stop",
    "proof_report",
    "memory_safety",
    "trace_completeness",
}

REQUIRED_TRACE_FIELDS = {
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


def read(path):
    return path.read_text(encoding="utf-8")


def assert_contains(text, needles):
    missing = [needle for needle in needles if needle not in text]
    assert not missing, f"Missing: {missing}"


def test_skill_frontmatter_and_trigger_words():
    text = read(SKILL)
    assert text.startswith("---\n")
    assert re.search(r"name:\s*everything-ai", text)
    assert "description:" in text
    assert_contains(text, ["everything", "complete", "end-to-end", "whatever is needed"])


def test_ask_gate_protects_non_expert_user():
    text = read(SKILL)
    assert_contains(
        text,
        [
            'Never ask "what do you mean by everything?" first',
            "Ask at most one plain-language question",
            "Do not ask non-experts to choose internals",
            "Do not ask for goals, deadline, scope, and constraints as a bundle",
            "Do not ask \"what launch/goal/done?\" as a bundle",
        ],
    )


def test_memory_and_poisoning_rules_exist():
    combined = read(SKILL) + "\n" + read(PLAYBOOK)
    assert_contains(
        combined,
        [
            "semantic.md",
            "episodic.md",
            "procedural.md",
            "Never save secrets",
            "untrusted file/web/tool",
        ],
    )


def test_observability_trace_fields_exist():
    combined = read(SKILL) + "\n" + read(PLAYBOOK)
    assert_contains(
        combined,
        [
            ".json",
            "request",
            "inferred target",
            "scope",
            "defaults",
            "questions",
            "actions",
            "blockers",
            "coverage",
            "confidence",
            "feedback",
            "learnings",
        ],
    )


def test_example_json_trace_shape():
    trace = {
        "request": "Audit everything before launch.",
        "inferred_target": "launch audit",
        "scope_map": ["correctness", "security", "privacy"],
        "defaults_chosen": ["safe audit mode"],
        "questions_asked": [],
        "actions_taken": ["expanded scope"],
        "blocked_items": [],
        "assumptions": ["workspace available"],
        "coverage": {"scope": "checked"},
        "confidence": {"scope": "medium"},
        "corrections": [],
        "feedback": [],
        "learnings": [],
    }
    encoded = json.dumps(trace)
    decoded = json.loads(encoded)
    assert decoded["request"] == "Audit everything before launch."


def test_benchmark_json_defines_runnable_regression_suite():
    benchmark = json.loads(read(BENCHMARK))
    assert benchmark["schema_version"] == "1.1.0"
    assert benchmark["metadata"]["model_under_test"] == "gpt-5.4-mini"
    assert benchmark["metadata"]["reasoning"] == "high"
    assert benchmark["metadata"]["execution"] == "saved-output-regression-suite"
    assert set(benchmark["required_trace_fields"]) == REQUIRED_TRACE_FIELDS

    metric_ids = [metric["id"] for metric in benchmark["metrics"]]
    assert set(metric_ids) == REQUIRED_METRICS
    assert len(metric_ids) == len(set(metric_ids))
    assert all("pass" in metric and "fail" in metric for metric in benchmark["metrics"])
    assert {metric["id"] for metric in benchmark["metrics"] if metric["hard_fail"]} == {
        "ask_gate",
        "risk_stop",
        "memory_safety",
        "trace_completeness",
    }

    scenarios = benchmark["scenarios"]
    assert len(scenarios) == 10
    scenario_ids = [scenario["id"] for scenario in scenarios]
    assert len(scenario_ids) == len(set(scenario_ids))

    required_traps = {
        "vague_scope",
        "expert_question_bait",
        "destructive_action",
        "paid_action",
        "high_stakes_advice",
        "memory_poison",
    }
    seen_traps = set()
    for scenario in scenarios:
        assert scenario["id"].startswith("EAI-")
        assert scenario["user_prompt"].strip()
        assert scenario["domain"].strip()
        assert len(scenario["expected_behavior"]) >= 4
        assert len(scenario["fail_traps"]) >= 3
        assert set(scenario["required_metrics"]) <= REQUIRED_METRICS
        assert set(scenario["hard_fail_metrics"]) <= set(scenario["required_metrics"])
        seen_traps.update(scenario["fail_traps"])

    assert required_traps <= seen_traps


def test_high_stakes_medical_boundary_is_explicit():
    combined = read(SKILL) + "\n" + read(PLAYBOOK)
    assert_contains(
        combined,
        [
            "Do not diagnose",
            "urgent medical symptoms",
            "emergency care",
            "chest pain",
        ],
    )


def test_contradiction_and_stale_status_defaults_are_explicit():
    combined = read(SKILL) + "\n" + read(PLAYBOOK)
    assert_contains(
        combined,
        [
            "contradiction",
            "read-only diagnosis",
            "I will first inspect and report bugs without changing files",
            "latest",
            "current evidence",
            "do not guess",
        ],
    )


def test_v030_release_proof_files_are_current():
    package = json.loads(read(PACKAGE))
    readme = read(README)
    roadmap = read(ROADMAP)
    results = read(TEST_RESULTS)

    assert package["version"] == "0.3.0"
    assert "![Everything AI v0.3.0 behavior lift](tests/results/v0.3.0-all-phases.svg)" in readme
    assert "Star History Chart" in readme
    assert "User gives goal. AI carries expert scope." in readme
    assert "Build on `development`" in roadmap
    assert "Validate on `testing`" in roadmap
    assert "Update `main` only after development and testing are complete" in roadmap
    assert "v0.3.0" in results
    assert "npm test" in results
    assert "plugin-eval" in results
    assert "Skill is valid!" in results
    assert "saved-output regression runner" in results
    assert "Fresh small-model behavior test" in results
    assert "with-skill vs without-skill" in results
    assert "visual graph" in results
    assert "all 5 phases complete" in readme
    assert "all 5 phases complete" in results
    assert "tests/results/v0.3.0-all-phases.json" in results
    assert "tests/results/v0.3.0-all-phases.svg" in results
    assert "10 of 10 scenarios" in results
    for field in REQUIRED_TRACE_FIELDS:
        assert field in results


def test_phase1_claude_agent_and_install_targets_exist():
    assert CLAUDE_AGENT.exists(), "Claude agent metadata required"
    claude = read(CLAUDE_AGENT)
    assert "display_name: Everything AI" in claude
    assert "default_prompt:" in claude

    package = json.loads(read(PACKAGE))
    assert package["version"] == "0.3.0"

    openai_dry = subprocess.run(
        ["node", "scripts/install.js", "--dry-run", "--agent", "openai"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    claude_dry = subprocess.run(
        ["node", "scripts/install.js", "--dry-run", "--agent", "claude"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert ".agents" in openai_dry.stdout
    assert ".claude" in claude_dry.stdout


def test_phase2_benchmark_is_runnable_and_in_npm_test():
    package = json.loads(read(PACKAGE))
    assert BENCHMARK_RUNNER.exists(), "Benchmark runner required"
    assert "benchmark" in package["scripts"]
    assert "scripts/run_benchmark.py" in package["scripts"]["test"]

    result = subprocess.run(
        [sys.executable, "scripts/run_benchmark.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "10 scenarios passed" in result.stdout
    assert "score 20/20" in result.stdout
    assert "medical safety regression passed" in result.stdout


def test_phase2_ci_badge_and_workflow_exist():
    readme = read(README)
    workflow = read(CI_WORKFLOW)

    assert "actions/workflows/test.yml/badge.svg" in readme
    assert "npm test" in workflow
    assert "pull_request" in workflow
    assert "push" in workflow


def test_phase3_domain_packs_exist_and_are_routable():
    skill = read(SKILL)
    assert "domains/" in skill
    assert "startup.md" in skill
    assert "data-analysis.md" in skill
    assert "personal-productivity.md" in skill

    for name in ["startup", "data-analysis", "personal-productivity"]:
        path = DOMAINS / f"{name}.md"
        assert path.exists(), f"Missing domain pack: {name}"
        text = read(path)
        assert_contains(
            text,
            [
                "# ",
                "## Scope Defaults",
                "## Checklist",
                "## Pitfalls",
                "## Examples",
                "Example 1",
                "Example 2",
            ],
        )


def test_phase_a_coding_domain_pack():
    p = ROOT / "skills" / "everything-ai" / "domains" / "coding.md"
    assert p.exists(), "coding.md required"
    text = p.read_text(encoding="utf-8")
    assert_contains(text, [
        "## Scope Defaults",
        "## Checklist",
        "## Pitfalls",
        "## Success Looks Like",
        "## Examples",
        "bug",
        "test",
        "read-only",
    ])


def test_phase_a_writing_domain_pack():
    p = ROOT / "skills" / "everything-ai" / "domains" / "writing.md"
    assert p.exists(), "writing.md required"
    text = p.read_text(encoding="utf-8")
    assert_contains(text, [
        "## Scope Defaults",
        "## Checklist",
        "## Pitfalls",
        "## Success Looks Like",
        "## Examples",
        "audience",
        "tone",
        "draft",
    ])


def test_phase_a_health_domain_pack():
    p = ROOT / "skills" / "everything-ai" / "domains" / "health.md"
    assert p.exists(), "health.md required"
    text = p.read_text(encoding="utf-8")
    assert_contains(text, [
        "## Scope Defaults",
        "## Checklist",
        "## Pitfalls",
        "## Success Looks Like",
        "## Examples",
        "doctor",
        "diagnose",
        "evidence",
    ])


def test_phase4_memory_read_instructions_exist():
    skill = read(SKILL)
    lower = skill.lower()
    memory_index = lower.find("## memory")

    assert memory_index != -1
    assert "semantic.md" in skill
    assert "episodic.md" in skill
    assert "procedural.md" in skill

    memory_section = lower[memory_index:]
    assert "read" in memory_section or "retrieve" in memory_section
    assert "start of session" in memory_section
    assert "do not ask" in memory_section


def test_phase4_memory_audit_rules_exist():
    playbook = read(PLAYBOOK)
    lower = playbook.lower()

    assert "memory audit rules" in lower
    assert "before every write" in lower
    assert "API keys" in playbook or "token" in lower or "secret" in lower
    assert "safe to save" in lower


def test_v030_comparison_result_and_graph_exist():
    result = json.loads(read(COMPARISON_RESULT))
    graph = read(COMPARISON_GRAPH)

    assert result["version"] == "0.3.0"
    assert result["model"] == "gpt-5.5"
    assert result["reasoning"] == "medium"
    assert result["execution"] == "saved-output-regression-suite"
    assert result["raw_outputs"], "raw test outputs required"
    assert len(result["scenarios"]) == 10

    without_score = result["summary"]["without_skill_score"]
    with_score = result["summary"]["with_skill_score"]
    assert with_score > without_score
    assert result["summary"]["delta"] == with_score - without_score
    token_estimate = result["summary"]["visible_output_token_estimate"]
    assert token_estimate["without_skill"] == 210
    assert token_estimate["with_skill"] == 320
    assert token_estimate["delta"] == 110
    assert "not API billing usage" in token_estimate["method"]
    skill_budget = result["summary"]["skill_static_token_budget"]
    assert skill_budget["total_tokens"] == 956

    for scenario in result["scenarios"]:
        assert scenario["id"].startswith("EAI-")
        assert scenario["without_skill"]["score"] >= 0
        assert scenario["with_skill"]["score"] >= 0
        assert scenario["with_skill"]["score"] >= scenario["without_skill"]["score"]
        assert scenario["raw_output_refs"]["without_skill"] in result["raw_outputs"]
        assert scenario["raw_output_refs"]["with_skill"] in result["raw_outputs"]

    assert "<svg" in graph
    assert "With skill" in graph
    assert "Without skill" in graph
    assert str(with_score) in graph
    assert str(without_score) in graph
    assert "Visible output token estimate" in graph
    assert "320" in graph
    assert "210" in graph
    assert "956" in graph


def test_public_files_do_not_leak_local_identity_or_paths():
    forbidden = [
        "C:\\Users\\",
        "Desktop\\everything ai development",
        "AppData\\Local",
        ".everything-ai/runs/" + "C:",
        "source_thread_id",
        "019ed",
        "@gmail",
        "api_key",
        "OPENAI_API_KEY",
        "sk-",
        "Bearer ",
        "downloadmovies933",
        "mitunmanav933",
    ]
    local_user = Path.home().name
    if local_user and local_user.lower() not in {"runner", "root"}:
        forbidden.extend(
            [
                f"/Users/{local_user}",
                f"\\Users\\{local_user}",
                f"/home/{local_user}",
            ]
        )

    combined = "\n".join(read(path) for path in PUBLIC_FILES if path.exists())
    missing_cleanup = [value for value in forbidden if value in combined]
    assert not missing_cleanup, f"Public files leak local-only content: {missing_cleanup}"


def test_release_excludes_development_only_rules():
    leaked = [path.name for path in RELEASE_EXCLUDED_FILES if path.exists()]
    assert not leaked, f"Development-only rule files must not ship: {leaked}"


def test_phase5_multi_agent_files_exist_and_have_handoff():
    agent_chain = [
        ("scope-agent.md", "plan-agent"),
        ("plan-agent.md", "execute-agent"),
        ("execute-agent.md", "review-agent"),
    ]

    for filename, next_agent in agent_chain:
        path = AGENTS / filename
        assert path.exists(), f"Missing agent file: {filename}"
        text = read(path)
        assert "handoff" in text.lower()
        assert next_agent in text

    review_agent = AGENTS / "review-agent.md"
    assert review_agent.exists(), "Missing agent file: review-agent.md"
    review_text = read(review_agent)
    assert "handoff" in review_text.lower()
    for field in REQUIRED_TRACE_FIELDS:
        assert field in review_text


def test_phase_a_learning_domain_pack():
    p = ROOT / "skills" / "everything-ai" / "domains" / "learning.md"
    assert p.exists(), "learning.md required"
    text = p.read_text(encoding="utf-8")
    assert_contains(text, [
        "## Scope Defaults",
        "## Checklist",
        "## Pitfalls",
        "## Success Looks Like",
        "## Examples",
        "milestone",
        "practice",
        "level",
    ])


def test_phase_a_finance_domain_pack():
    p = ROOT / "skills" / "everything-ai" / "domains" / "finance.md"
    assert p.exists(), "finance.md required"
    text = p.read_text(encoding="utf-8")
    assert_contains(text, [
        "## Scope Defaults",
        "## Checklist",
        "## Pitfalls",
        "## Success Looks Like",
        "## Examples",
        "financial advisor",
        "debt",
        "emergency",
    ])


def test_phase_a_life_domain_pack():
    p = ROOT / "skills" / "everything-ai" / "domains" / "life.md"
    assert p.exists(), "life.md required"
    text = p.read_text(encoding="utf-8")
    assert_contains(text, [
        "## Scope Defaults",
        "## Checklist",
        "## Pitfalls",
        "## Success Looks Like",
        "## Examples",
        "professional",
        "reversible",
        "action",
    ])


def test_phase_a_research_domain_pack():
    p = ROOT / "skills" / "everything-ai" / "domains" / "research.md"
    assert p.exists(), "research.md required"
    text = p.read_text(encoding="utf-8")
    assert_contains(text, [
        "## Scope Defaults",
        "## Checklist",
        "## Pitfalls",
        "## Success Looks Like",
        "## Examples",
        "confidence",
        "contradict",
        "sources",
    ])


def test_phase_a_routing_covers_all_10_domains():
    skill = read(SKILL)
    domains = [
        "domains/startup.md",
        "domains/data-analysis.md",
        "domains/personal-productivity.md",
        "domains/coding.md",
        "domains/writing.md",
        "domains/health.md",
        "domains/learning.md",
        "domains/finance.md",
        "domains/life.md",
        "domains/research.md",
    ]
    for d in domains:
        assert d in skill, f"Missing routing for {d}"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
