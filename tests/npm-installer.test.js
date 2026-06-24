const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const test = require("node:test");

const PACKAGE_ROOT = path.resolve(__dirname, "..");
const CLI = path.join(PACKAGE_ROOT, "bin", "hf-weekly-skill.js");
const SKILL_NAME = "writing-hf-weekly-digest";

function tempDir(t) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "hf-weekly-skill-"));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  return directory;
}

function run(args, options = {}) {
  return spawnSync(process.execPath, [CLI, ...args], {
    cwd: PACKAGE_ROOT,
    encoding: "utf8",
    env: { ...process.env, ...options.env },
  });
}

test("path uses CODEX_HOME/skills by default", (t) => {
  const codexHome = tempDir(t);
  const result = run(["path"], { env: { CODEX_HOME: codexHome } });

  assert.equal(result.status, 0, result.stderr);
  assert.equal(
    result.stdout.trim(),
    path.join(codexHome, "skills", SKILL_NAME),
  );
});

test("path accepts a custom skills directory", (t) => {
  const target = tempDir(t);
  const result = run(["path", "--target", target]);

  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout.trim(), path.join(target, SKILL_NAME));
});

test("install copies the complete runtime Skill payload", (t) => {
  const target = tempDir(t);
  const result = run(["install", "--target", target]);
  const destination = path.join(target, SKILL_NAME);

  assert.equal(result.status, 0, result.stderr);
  for (const relative of [
    "SKILL.md",
    "agents/openai.yaml",
    "references/visual-workflow.md",
    "scripts/fetch_hf_week.py",
    "scripts/collect_paper_figures.py",
    "scripts/render_wechat.py",
  ]) {
    assert.equal(
      fs.existsSync(path.join(destination, relative)),
      true,
      `missing ${relative}`,
    );
  }
  assert.equal(fs.existsSync(path.join(destination, "tests")), false);
  assert.equal(fs.existsSync(path.join(destination, "package.json")), false);
});

test("install refuses to overwrite an existing Skill", (t) => {
  const target = tempDir(t);
  assert.equal(run(["install", "--target", target]).status, 0);

  const result = run(["install", "--target", target]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /already exists/i);
});

test("install --force replaces an existing Skill", (t) => {
  const target = tempDir(t);
  const destination = path.join(target, SKILL_NAME);
  assert.equal(run(["install", "--target", target]).status, 0);
  fs.writeFileSync(path.join(destination, "stale.txt"), "old");

  const result = run(["install", "--target", target, "--force"]);

  assert.equal(result.status, 0, result.stderr);
  assert.equal(fs.existsSync(path.join(destination, "stale.txt")), false);
  assert.equal(fs.existsSync(path.join(destination, "SKILL.md")), true);
});

test("update atomically replaces an installed Skill", (t) => {
  const target = tempDir(t);
  const destination = path.join(target, SKILL_NAME);
  assert.equal(run(["install", "--target", target]).status, 0);
  fs.writeFileSync(path.join(destination, "stale.txt"), "old");

  const result = run(["update", "--target", target]);

  assert.equal(result.status, 0, result.stderr);
  assert.equal(fs.existsSync(path.join(destination, "stale.txt")), false);
  assert.equal(fs.existsSync(path.join(destination, "SKILL.md")), true);
});

test("update reports a missing installation", (t) => {
  const target = tempDir(t);
  const result = run(["update", "--target", target]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /not installed/i);
});

test("uninstall removes only the installed Skill directory", (t) => {
  const target = tempDir(t);
  const destination = path.join(target, SKILL_NAME);
  const sentinel = path.join(target, "keep-me.txt");
  fs.writeFileSync(sentinel, "keep");
  assert.equal(run(["install", "--target", target]).status, 0);

  const result = run(["uninstall", "--target", target]);

  assert.equal(result.status, 0, result.stderr);
  assert.equal(fs.existsSync(destination), false);
  assert.equal(fs.readFileSync(sentinel, "utf8"), "keep");
});

test("unknown commands fail with usage guidance", () => {
  const result = run(["explode"]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /usage:/i);
});
