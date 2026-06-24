from pathlib import Path
import json
import os
import re
import subprocess
import sys
import tempfile


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
    assert len(scenarios) == 20
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
    eai_scenarios = [s for s in scenarios if s["id"].startswith("EAI-")]
    for scenario in eai_scenarios:
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


def test_v041_release_proof_files_are_current():
    package = json.loads(read(PACKAGE))
    readme = read(README)
    roadmap = read(ROADMAP)
    results = read(TEST_RESULTS)

    assert package["version"] == "0.4.1"
    assert 'src="tests/results/v0.4.1-fixed.svg"' in readme
    assert "## v0.4.1 Status" in readme
    assert "## Numbers" in readme
    assert "blind cross-model judge" in readme
    assert "35/35 unit tests green" in readme
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
    assert package["version"] == "0.4.1"

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
    assert "20 scenarios passed" in result.stdout
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


def test_v040_comparison_result_and_graph_exist():
    result = json.loads(read(ROOT / "tests" / "results" / "v0.4.0-all-phases.json"))
    graph = read(ROOT / "tests" / "results" / "v0.4.0-all-phases.svg")

    assert result["version"] == "0.4.0"
    assert result["summary"]["tests_passed"] == 32
    assert result["summary"]["tests_total"] == 32
    assert result["summary"]["domains"] == 10
    assert result["summary"]["benchmark_scenarios"] == 20
    assert len(result["domains"]) == 10

    lift = result["summary"]["behavior_lift"]
    assert lift["model"] == "gpt-5.5"
    assert lift["reasoning"] == "medium"
    assert lift["without_skill_pct"] == 88.2
    assert lift["with_skill_pct"] == 92.1
    assert lift["delta_pct"] == 3.9
    assert lift["weak_model"] == "gpt-5.4-mini"
    assert lift["weak_delta_pct"] == -10.5

    # live aggregate the graph is generated from
    live = json.loads(read(ROOT / "tests" / "results" / "v0.4.0-live-run.json"))
    assert live["models"]["gpt-5.5"]["reasoning"] == "medium"
    assert live["models"]["gpt-5.4-mini"]["reasoning"] == "low"
    assert live["models"]["gpt-5.5"]["skill_on"]["pct"] == 92.1
    assert live["models"]["gpt-5.4-mini"]["reran"] == live["models"]["gpt-5.4-mini"]["failed_runs"]

    assert "<svg" in graph
    assert "blind cross-model judge" in graph
    assert "gpt-5.5" in graph
    assert "gpt-5.4-mini" in graph
    assert "skill helps" in graph
    assert "skill hurts" in graph
    assert "88.2" in graph and "92.1" in graph


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
    # Key-shaped secrets: real prefixes (sk-ant-, sk-proj-, sk-<long token>),
    # not the metric name "ask-gate". Word boundary avoids matching "ask-".
    if re.search(r"\bsk-[A-Za-z0-9]{8,}", combined):
        missing_cleanup.append("sk- key")
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


def test_phase_b_bootstrap_script_exists_and_creates_memory_files():
    import subprocess, tempfile, os
    bootstrap = ROOT / "scripts" / "bootstrap-memory.js"
    assert bootstrap.exists(), "bootstrap-memory.js required"

    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            ["node", str(bootstrap), "--dir", tmp],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        for name in ["semantic.md", "episodic.md", "procedural.md"]:
            p = os.path.join(tmp, name)
            assert os.path.exists(p), f"Missing: {name}"
            content = open(p).read()
            assert "## " in content, f"{name} must have sections"


def test_phase_c_quickstart_exists_and_has_examples():
    p = ROOT / "QUICKSTART.md"
    assert p.exists(), "QUICKSTART.md required"
    text = p.read_text(encoding="utf-8")
    assert_contains(text, [
        "## What it does",
        "## How to use",
        "## Examples",
        "## What it will do",
        "## When it will ask",
    ])


def test_phase_c_plain_language_rule_in_skill():
    skill = read(SKILL)
    assert_contains(skill, [
        "plain language",
        "No jargon",
    ])


def test_phase_d_context_hook_exists_and_outputs_valid_json():
    import subprocess, json, os
    hook = ROOT / "skills" / "everything-ai" / "hooks" / "context_inject.py"
    hooks_config = ROOT / "skills" / "everything-ai" / "hooks" / "hooks.json"
    assert hook.exists(), "context_inject.py required"
    assert hooks_config.exists(), "hooks/hooks.json required"

    payload = json.dumps({
        "session_id": "test-session",
        "cwd": "/tmp",
        "hook_event_name": "UserPromptSubmit",
        "turn_id": "t1",
        "prompt": "do everything",
        "model": "gpt-4",
        "permission_mode": "default",
    })
    result = subprocess.run(
        [sys.executable, str(hook)],
        input=payload,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    out = json.loads(result.stdout)
    assert "hookSpecificOutput" in out
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert "Today" in ctx
    assert "directory" in ctx.lower() or "Directory" in ctx


def test_phase_d_skill_lite_exists_and_is_compact():
    lite = ROOT / "skills" / "everything-ai" / "SKILL.lite.md"
    assert lite.exists(), "SKILL.lite.md must exist for small model support"
    text = lite.read_text(encoding="utf-8")
    assert len(text) < 2000, f"SKILL.lite.md must be under 2000 chars, got {len(text)}"
    assert "Infer" in text or "infer" in text, "lite skill must include infer/ask rule"
    assert "Stop" in text or "stop" in text, "lite skill must include stop-before-risk rule"
    assert "Report" in text or "report" in text, "lite skill must include report rule"
    assert "domains/coding.md" not in text, "lite skill must not include domain routing"
    assert "scope-agent" not in text, "lite skill must not include agent chain references"


def test_phase_d_context_hook_injects_memory_when_files_exist(tmp_path):
    import subprocess, json, os
    (tmp_path / "semantic.md").write_text("User prefers TypeScript.", encoding="utf-8")
    (tmp_path / "episodic.md").write_text("Fixed login bug in session 3.", encoding="utf-8")
    (tmp_path / "procedural.md").write_text("", encoding="utf-8")  # empty — must not appear

    hook = ROOT / "skills" / "everything-ai" / "hooks" / "context_inject.py"
    payload = json.dumps({"cwd": "/tmp/test"})
    result = subprocess.run(
        [sys.executable, str(hook)],
        input=payload,
        capture_output=True,
        text=True,
        env={**os.environ, "EVERYTHING_AI_MEMORY_DIR": str(tmp_path)},
    )
    assert result.returncode == 0, result.stderr
    out = json.loads(result.stdout)
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert "User prefers TypeScript." in ctx
    assert "Fixed login bug in session 3." in ctx
    assert "[Memory: semantic.md]" in ctx
    assert "[Memory: episodic.md]" in ctx
    assert "[Memory: procedural.md]" not in ctx


def test_phase_b_plugin_data_not_used_as_memory_dir():
    """Regression guard: PLUGIN_DATA must never be used as the memory directory.
    PLUGIN_DATA is the plugin installation dir (e.g. superpowers/6.0.3/) — it
    contains no memory files. Using it silenced the hook on every Codex prompt,
    causing the scope_inference/safe_defaults -10.5% regression in v0.4.0."""
    import json, subprocess, sys, tempfile
    from pathlib import Path

    hook = ROOT / "skills" / "everything-ai" / "hooks" / "context_inject.py"

    with tempfile.TemporaryDirectory() as plugin_dir, \
         tempfile.TemporaryDirectory() as mem_dir:

        # Put a real memory file in the memory dir
        (Path(mem_dir) / "semantic.md").write_text("user prefers plain language")

        # Put a decoy file in PLUGIN_DATA dir (should be ignored)
        (Path(plugin_dir) / "semantic.md").write_text("DECOY — should not appear")

        env = {
            **__import__("os").environ,
            "PLUGIN_DATA": plugin_dir,
            "EVERYTHING_AI_MEMORY_DIR": mem_dir,
        }
        payload = json.dumps({"cwd": "/tmp"})
        result = subprocess.run(
            [sys.executable, str(hook)],
            input=payload, capture_output=True, text=True, env=env
        )
        assert result.returncode == 0, result.stderr
        ctx = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]

        assert "plain language" in ctx, "Memory from EVERYTHING_AI_MEMORY_DIR must be injected"
        assert "DECOY" not in ctx, "PLUGIN_DATA must never be used as memory dir"


def test_v042_halt_vs_guess_gate_in_scope_agent():
    text = (AGENTS / "scope-agent.md").read_text(encoding="utf-8")
    assert_contains(text, [
        "## Ambiguity Gate",
        "irreversible",
        "proceed",
        "state the assumption",
        "HALT",
    ])


def test_v042_halt_vs_guess_gate_in_execute_agent():
    text = (AGENTS / "execute-agent.md").read_text(encoding="utf-8")
    assert_contains(text, [
        "## Execution Gate",
        "irreversible",
        "reversible",
        "HALT",
        "explicitly requested",
    ])


def test_v042_memory_write_hook_exists_and_registered():
    hook = ROOT / "skills" / "everything-ai" / "hooks" / "memory_write.py"
    assert hook.exists(), "memory_write.py required"
    cfg = json.loads((ROOT / "skills" / "everything-ai" / "hooks" / "hooks.json").read_text())
    assert "Stop" in cfg["hooks"], "Stop hook must be registered in hooks.json"


def test_v042_memory_write_writes_correction_to_procedural(tmp_path):
    hook = ROOT / "skills" / "everything-ai" / "hooks" / "memory_write.py"
    payload = json.dumps({
        "transcript": [
            {"role": "user", "content": "no, that's wrong, do it differently"}
        ]
    })
    result = subprocess.run(
        [sys.executable, str(hook)],
        input=payload, capture_output=True, text=True,
        env={**os.environ, "EVERYTHING_AI_MEMORY_DIR": str(tmp_path)},
    )
    assert result.returncode == 0, result.stderr
    procedural = tmp_path / "procedural.md"
    assert procedural.exists(), "procedural.md must be created on correction"
    assert "wrong" in procedural.read_text(encoding="utf-8")


def test_v042_memory_write_silent_on_non_correction(tmp_path):
    hook = ROOT / "skills" / "everything-ai" / "hooks" / "memory_write.py"
    payload = json.dumps({
        "transcript": [
            {"role": "user", "content": "help me plan my week"}
        ]
    })
    result = subprocess.run(
        [sys.executable, str(hook)],
        input=payload, capture_output=True, text=True,
        env={**os.environ, "EVERYTHING_AI_MEMORY_DIR": str(tmp_path)},
    )
    assert result.returncode == 0, result.stderr
    procedural = tmp_path / "procedural.md"
    # Non-correction must not write to procedural
    if procedural.exists():
        assert "help me plan" not in procedural.read_text(encoding="utf-8")


def test_v042_memory_write_uses_transcript_path_when_present(tmp_path):
    import tempfile, json as _json
    hook = ROOT / "skills" / "everything-ai" / "hooks" / "memory_write.py"
    # Write a JSONL transcript file
    transcript_file = tmp_path / "transcript.jsonl"
    transcript_file.write_text(
        _json.dumps({"role": "assistant", "content": "Here is my answer."}) + "\n" +
        _json.dumps({"role": "user", "content": "no, that's wrong"}) + "\n",
        encoding="utf-8",
    )
    mem_dir = tmp_path / "mem"
    mem_dir.mkdir()
    payload = _json.dumps({"transcript_path": str(transcript_file)})
    result = subprocess.run(
        [sys.executable, str(hook)],
        input=payload, capture_output=True, text=True,
        env={**os.environ, "EVERYTHING_AI_MEMORY_DIR": str(mem_dir)},
    )
    assert result.returncode == 0, result.stderr
    procedural = mem_dir / "procedural.md"
    assert procedural.exists(), "procedural.md must be written when correction found via transcript_path"
    assert "wrong" in procedural.read_text(encoding="utf-8")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            if fn.__code__.co_argcount == 1:
                with tempfile.TemporaryDirectory() as tmp:
                    fn(Path(tmp))
            else:
                fn()
            print(f"ok {name}")


def test_v042_all_agents_have_next_agent_in_output():
    for filename in ["scope-agent.md", "plan-agent.md", "execute-agent.md", "review-agent.md"]:
        text = (AGENTS / filename).read_text(encoding="utf-8")
        assert "next_agent" in text, f"Missing next_agent field in {filename}"


def test_v042_review_agent_has_consistency_check():
    text = (AGENTS / "review-agent.md").read_text(encoding="utf-8")
    assert_contains(text, [
        "## Consistency Check",
        "episodic.md",
        "prior sessions",
    ])


def test_v042_all_domains_have_frameworks_and_live_facts():
    domain_names = [
        "startup", "coding", "personal-productivity", "health",
        "finance", "learning", "writing", "research", "data-analysis", "life",
    ]
    for name in domain_names:
        path = DOMAINS / f"{name}.md"
        assert path.exists(), f"Missing domain: {name}"
        text = path.read_text(encoding="utf-8")
        assert "## Frameworks" in text, f"Missing ## Frameworks in {name}.md"
        assert "## Live Facts" in text, f"Missing ## Live Facts in {name}.md"
