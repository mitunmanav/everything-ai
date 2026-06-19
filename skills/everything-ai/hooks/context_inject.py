#!/usr/bin/env python3
import sys
import json
import os
from datetime import date

data = json.load(sys.stdin)

today = date.today().strftime("%A, %B %d, %Y")
cwd = data.get("cwd", os.getcwd())

context = f"Today is {today}. Current directory: {cwd}."

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": context,
    }
}))
