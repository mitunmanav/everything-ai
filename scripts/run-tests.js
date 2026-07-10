#!/usr/bin/env node

const { spawnSync } = require("child_process");

const pythonCommands = [
  { cmd: "python3", args: ["-m", "pytest", "tests/test_everything_ai.py", "-v"] },
  { cmd: "python", args: ["-m", "pytest", "tests/test_everything_ai.py", "-v"] },
  { cmd: "py", args: ["-3", "-m", "pytest", "tests/test_everything_ai.py", "-v"] },
];

function run(command, args) {
  return spawnSync(command, args, { stdio: "inherit" });
}

function runPythonTests() {
  for (const entry of pythonCommands) {
    const result = run(entry.cmd, entry.args);
    if (!result.error && result.status === 0) return;
  }
  console.error("Failed to run pytest with python3, python, or py -3.");
  process.exit(1);
}

runPythonTests();

const installDryRun = run("node", ["scripts/install.js", "--dry-run"]);
if (installDryRun.status !== 0) process.exit(installDryRun.status || 1);
