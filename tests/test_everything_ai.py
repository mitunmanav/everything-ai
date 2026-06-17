from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "everything-ai" / "SKILL.md"
PLAYBOOK = ROOT / "skills" / "everything-ai" / "references" / "playbook.md"


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


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
