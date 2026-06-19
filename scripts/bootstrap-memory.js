#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const os = require("os");

function valueAfter(flag) {
  const raw = process.argv.slice(2);
  const i = raw.indexOf(flag);
  return i >= 0 ? raw[i + 1] : null;
}

const dir = valueAfter("--dir") || path.join(os.homedir(), ".agents", "skills", "everything-ai");

const files = {
  "semantic.md": `# Semantic Memory\n\nStable preferences and domain facts the agent should always apply.\n\n## User Preferences\n\n(none yet — preferences are added when the user explicitly states them multiple times)\n\n## Domain Facts\n\n(none yet)\n`,
  "episodic.md": `# Episodic Memory\n\nSummaries of past sessions and corrections.\n\n## Sessions\n\n(none yet — session summaries are added after significant work is completed)\n`,
  "procedural.md": `# Procedural Memory\n\nRecurring workflow steps and tool sequences.\n\n## Workflows\n\n(none yet — workflows are added when a sequence is repeated across multiple sessions)\n`,
};

for (const [name, content] of Object.entries(files)) {
  const filePath = path.join(dir, name);
  if (!fs.existsSync(filePath)) {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, content, "utf8");
    console.log(`Created: ${filePath}`);
  } else {
    console.log(`Exists (skipped): ${filePath}`);
  }
}
