#!/usr/bin/env node

const fs = require("fs");
const os = require("os");
const path = require("path");
const readline = require("readline");

const args = new Set(process.argv.slice(2));
const dryRun = args.has("--dry-run");
const force = args.has("--force");
const hasFlags = process.argv.slice(2).some((arg) =>
  ["--agent", "--target", "--force", "--dry-run"].includes(arg),
);

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
const agentTargets = {
  openai: path.join(os.homedir(), ".agents", "skills", "everything-ai"),
  codex: path.join(os.homedir(), ".agents", "skills", "everything-ai"),
  claude: path.join(os.homedir(), ".claude", "skills", "everything-ai"),
};
let agent = valueAfter("--agent") || "codex";

function validateAgent(name) {
  if (agentTargets[name]) return;
  console.error(`Unknown agent: ${agent}`);
  console.error("Use --agent openai, --agent codex, or --agent claude.");
  process.exit(1);
}

function ask(rl, question) {
  return new Promise((resolve) => {
    const onClose = () => resolve(null);
    rl.once("close", onClose);
    rl.question(question, (answer) => {
      rl.off("close", onClose);
      resolve(answer.trim());
    });
  });
}

async function promptForInstall() {
  console.log("Everything AI Skill Installer");
  console.log("");

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const answer = await ask(
    rl,
    "Install for which agent? [claude/codex] (default: codex): ",
  );
  agent = answer || "codex";
  validateAgent(agent);

  const targetPath = valueAfter("--target") || agentTargets[agent];
  console.log(`Destination: ${targetPath}`);

  const confirm = await ask(rl, `Install to ${targetPath}? [Y/n]: `);
  rl.close();

  if (confirm !== "" && !["y", "yes"].includes((confirm || "").toLowerCase())) {
    console.log("Install cancelled.");
    process.exit(0);
  }

  return targetPath;
}

async function main() {
  validateAgent(agent);

  const target = hasFlags
    ? valueAfter("--target") || agentTargets[agent]
    : await promptForInstall();

  if (!fs.existsSync(path.join(source, "SKILL.md"))) {
    console.error("Everything AI skill files not found in package.");
    process.exit(1);
  }

  if (dryRun) {
    console.log(`Would install Everything AI skill to: ${target}`);
    process.exit(0);
  }

  if (fs.existsSync(target) && !force && hasFlags) {
    console.error(`Refusing to overwrite existing skill: ${target}`);
    console.error("Use --force to replace it, or --target <path> for another location.");
    process.exit(1);
  }

  copyDir(source, target);
  console.log(`Installed Everything AI skill to: ${target}`);
  const { execSync } = require("child_process");
  try {
    execSync(
      `node "${path.join(packageRoot, "scripts", "bootstrap-memory.js")}" --dir "${target}"`,
      { stdio: "inherit" }
    );
  } catch (e) {
    console.warn("Memory bootstrap failed (non-fatal):", e.message);
  }
  console.log("Done. Restart your agent to use the everything-ai skill.");
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
