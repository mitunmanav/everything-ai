#!/usr/bin/env python3
import sys
import json
import os
from datetime import date
from pathlib import Path

data = json.load(sys.stdin)

today = date.today().strftime("%A, %B %d, %Y")
cwd = data.get("cwd", os.getcwd())

if "PLUGIN_DATA" in os.environ:
    memory_dir = Path(os.environ["PLUGIN_DATA"])
elif "EVERYTHING_AI_MEMORY_DIR" in os.environ:
    memory_dir = Path(os.environ["EVERYTHING_AI_MEMORY_DIR"])
else:
    memory_dir = Path.home() / ".agents" / "skills" / "everything-ai"

parts = [f"Today is {today}. Current directory: {cwd}."]

MAX_MEMORY_CHARS = 1500
total_chars = 0
for name in ("semantic.md", "episodic.md", "procedural.md"):
    path = memory_dir / name
    if path.exists():
        content = path.read_text(encoding="utf-8").strip()
        if content and total_chars < MAX_MEMORY_CHARS:
            chunk = content[: MAX_MEMORY_CHARS - total_chars]
            parts.append(f"\n[Memory: {name}]\n{chunk}")
            total_chars += len(chunk)

context = "\n".join(parts)

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": context,
    }
}))
