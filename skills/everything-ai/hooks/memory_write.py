#!/usr/bin/env python3
import sys
import json
import os
from datetime import date
from pathlib import Path

data = json.load(sys.stdin)

if "EVERYTHING_AI_MEMORY_DIR" in os.environ:
    memory_dir = Path(os.environ["EVERYTHING_AI_MEMORY_DIR"])
else:
    memory_dir = Path.home() / ".agents" / "skills" / "everything-ai"

memory_dir.mkdir(parents=True, exist_ok=True)

CORRECTION_SIGNALS = [
    "no,", "no.", "wrong", "not like that", "differently",
    "stop doing", "don't do", "never do", "not that", "that's not",
    "incorrect", "instead", "you should not", "do not do",
]
COMPLETION_SIGNALS = [
    "thank", "perfect", "great job", "done", "excellent", "looks good",
    "that's it", "that works", "exactly", "nailed it",
]

today = date.today().strftime("%Y-%m-%d")
transcript = data.get("transcript", [])

last_user_msg = ""
for turn in reversed(transcript):
    if not isinstance(turn, dict):
        continue
    if turn.get("role") != "user":
        continue
    content = turn.get("content", "")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                last_user_msg = block.get("text", "")
                break
    elif isinstance(content, str):
        last_user_msg = content
    if last_user_msg:
        break

if not last_user_msg:
    sys.exit(0)

msg_lower = last_user_msg.lower()
is_correction = any(signal in msg_lower for signal in CORRECTION_SIGNALS)
is_completion = any(signal in msg_lower for signal in COMPLETION_SIGNALS)

if is_correction:
    procedural_path = memory_dir / "procedural.md"
    entry = f"- [{today}] {last_user_msg.strip()}\n"
    with open(procedural_path, "a", encoding="utf-8") as f:
        f.write(entry)
elif is_completion:
    episodic_path = memory_dir / "episodic.md"
    entry = f"- [{today}] session completed successfully\n"
    with open(episodic_path, "a", encoding="utf-8") as f:
        f.write(entry)
# else: silent — no write
