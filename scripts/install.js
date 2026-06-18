#!/usr/bin/env node

const fs = require("fs");
const os = require("os");
const path = require("path");

const args = new Set(process.argv.slice(2));
const dryRun = args.has("--dry-run");
const force = args.has("--force");

function valueAfter(flag) {
  const raw = process.argv.slice(2);
  const index = raw.indexOf(flag);
  return index >= 0 ? raw[index + 1] : null;
}

function copyDir(source, target) {
  fs.mkdirSync(target, { recursive: true });
  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    const sourcePath = path.join(source, entry.name);
    const targetPath = path.join(target, entry.name);
    if (entry.isDirectory()) copyDir(sourcePath, targetPath);
    else fs.copyFileSync(sourcePath, targetPath);
  }
}

const packageRoot = path.resolve(__dirname, "..");
const source = path.join(packageRoot, "skills", "everything-ai");
const agent = valueAfter("--agent") || "openai";
const agentTargets = {
  openai: path.join(os.homedir(), ".codex", "skills", "everything-ai"),
  codex: path.join(os.homedir(), ".codex", "skills", "everything-ai"),
  claude: path.join(os.homedir(), ".claude", "skills", "everything-ai"),
};

if (!agentTargets[agent]) {
  console.error(`Unknown agent: ${agent}`);
  console.error("Use --agent openai, --agent codex, or --agent claude.");
  process.exit(1);
}

const target =
  valueAfter("--target") ||
  agentTargets[agent];

if (!fs.existsSync(path.join(source, "SKILL.md"))) {
  console.error("Everything AI skill files not found in package.");
  process.exit(1);
}

if (dryRun) {
  console.log(`Would install Everything AI skill to: ${target}`);
  process.exit(0);
}

if (fs.existsSync(target) && !force) {
  console.error(`Refusing to overwrite existing skill: ${target}`);
  console.error("Use --force to replace it, or --target <path> for another location.");
  process.exit(1);
}

copyDir(source, target);
console.log(`Installed Everything AI skill to: ${target}`);
