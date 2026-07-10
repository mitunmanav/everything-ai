#!/usr/bin/env node

const { execSync } = require("child_process");

const allowedPrefixes = [
  "package.json",
  "README.md",
  "LICENSE",
  "QUICKSTART.md",
  "scripts/install.js",
  "scripts/bootstrap-memory.js",
  "skills/everything-ai/",
];

function isAllowed(path) {
  return allowedPrefixes.some((prefix) => path === prefix || path.startsWith(prefix));
}

const output = execSync("npm pack --dry-run --json", { encoding: "utf8" });
const packs = JSON.parse(output);
const files = (packs[0] && packs[0].files) || [];
const names = files.map((f) => f.path).sort();
const blocked = names.filter((name) => !isAllowed(name));

if (blocked.length > 0) {
  console.error("Blocked: dev/internal files detected in public package:");
  blocked.forEach((name) => console.error(` - ${name}`));
  process.exit(1);
}

console.log("Public package guard passed. Only launch/public files included.");
