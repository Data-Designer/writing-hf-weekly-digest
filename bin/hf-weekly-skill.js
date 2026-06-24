#!/usr/bin/env node

"use strict";

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const SKILL_NAME = "writing-hf-weekly-digest";
const PACKAGE_ROOT = path.resolve(__dirname, "..");
const PAYLOAD = ["SKILL.md", "agents", "references", "scripts"];
const COMMANDS = new Set(["install", "update", "uninstall", "path"]);

function usage() {
  return `Usage:
  hf-weekly-skill install [--target <skills-directory>] [--force]
  hf-weekly-skill update [--target <skills-directory>]
  hf-weekly-skill uninstall [--target <skills-directory>]
  hf-weekly-skill path [--target <skills-directory>]`;
}

function parseArgs(argv) {
  const command = argv[0];
  if (!COMMANDS.has(command)) {
    throw new Error(usage());
  }

  let target;
  let force = false;
  for (let index = 1; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--target") {
      target = argv[index + 1];
      if (!target || target.startsWith("--")) {
        throw new Error("--target requires a directory.\n\n" + usage());
      }
      index += 1;
    } else if (argument === "--force") {
      force = true;
    } else if (argument === "--help" || argument === "-h") {
      return { help: true };
    } else {
      throw new Error(`Unknown option: ${argument}\n\n${usage()}`);
    }
  }

  if (force && command !== "install") {
    throw new Error("--force is supported only by install.\n\n" + usage());
  }
  return { command, force, target };
}

function skillsDirectory(target) {
  if (target) {
    return path.resolve(target);
  }
  const codexHome = process.env.CODEX_HOME
    ? path.resolve(process.env.CODEX_HOME)
    : path.join(os.homedir(), ".codex");
  return path.join(codexHome, "skills");
}

function destinationFor(target) {
  return path.join(skillsDirectory(target), SKILL_NAME);
}

function copyPayload(destination) {
  fs.mkdirSync(destination, { recursive: true });
  for (const relative of PAYLOAD) {
    const source = path.join(PACKAGE_ROOT, relative);
    if (!fs.existsSync(source)) {
      throw new Error(`Package payload is incomplete: missing ${relative}`);
    }
    fs.cpSync(source, path.join(destination, relative), {
      recursive: true,
      errorOnExist: true,
      force: false,
    });
  }
}

function atomicReplace(destination) {
  const parent = path.dirname(destination);
  const suffix = `${process.pid}-${Date.now()}`;
  const staging = `${destination}.tmp-${suffix}`;
  const backup = `${destination}.backup-${suffix}`;
  const hadExisting = fs.existsSync(destination);

  fs.mkdirSync(parent, { recursive: true });
  try {
    copyPayload(staging);
    if (hadExisting) {
      fs.renameSync(destination, backup);
    }
    fs.renameSync(staging, destination);
    if (hadExisting) {
      fs.rmSync(backup, { recursive: true, force: true });
    }
  } catch (error) {
    fs.rmSync(staging, { recursive: true, force: true });
    if (
      hadExisting &&
      fs.existsSync(backup) &&
      !fs.existsSync(destination)
    ) {
      fs.renameSync(backup, destination);
    }
    throw error;
  }
}

function install(destination, force) {
  if (fs.existsSync(destination) && !force) {
    throw new Error(
      `Skill already exists at ${destination}. Use install --force or update.`,
    );
  }
  atomicReplace(destination);
  process.stdout.write(`Installed ${SKILL_NAME} at ${destination}\n`);
}

function update(destination) {
  if (!fs.existsSync(destination)) {
    throw new Error(
      `Skill is not installed at ${destination}. Run hf-weekly-skill install.`,
    );
  }
  atomicReplace(destination);
  process.stdout.write(`Updated ${SKILL_NAME} at ${destination}\n`);
}

function uninstall(destination) {
  if (path.basename(destination) !== SKILL_NAME) {
    throw new Error("Refusing to remove an unexpected destination.");
  }
  if (!fs.existsSync(destination)) {
    process.stdout.write(`${SKILL_NAME} is not installed at ${destination}\n`);
    return;
  }
  fs.rmSync(destination, { recursive: true, force: true });
  process.stdout.write(`Uninstalled ${SKILL_NAME} from ${destination}\n`);
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    process.stdout.write(usage() + "\n");
    return;
  }

  const destination = destinationFor(options.target);
  if (options.command === "path") {
    process.stdout.write(destination + "\n");
  } else if (options.command === "install") {
    install(destination, options.force);
  } else if (options.command === "update") {
    update(destination);
  } else if (options.command === "uninstall") {
    uninstall(destination);
  }
}

try {
  main();
} catch (error) {
  process.stderr.write(`Error: ${error.message}\n`);
  process.exitCode = 1;
}
