import assert from "node:assert/strict";
import { execFile, execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { chmod, mkdtemp, readFile, realpath, rm, stat, symlink, writeFile } from "node:fs/promises";
import { readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";
import { marked } from "marked";
import TurndownService from "turndown";
import { atomicSave, readDocument, resolveMarkdown, unsupportedMarkdown } from "../lib.js";
import { createRichMdServer } from "../server.js";

const tool = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repo = path.resolve(tool, "../..");
const execFileAsync = promisify(execFile);

test("static browser requests require token cookie and API keeps bearer auth", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "rich-md-http-"));
  const dist = path.join(root, "dist");
  await import("node:fs/promises").then(({ mkdir }) => mkdir(dist));
  const file = path.join(root, "doc.md");
  await writeFile(file, "# private\n");
  await writeFile(path.join(dist, "index.html"), '<script src="/app.js"></script>');
  await writeFile(path.join(dist, "app.js"), "ok");
  const app = await createRichMdServer({ repo: root, file, token: "secret-token", dist });
  await new Promise((resolve) => app.server.listen(0, "127.0.0.1", resolve));
  const base = `http://127.0.0.1:${app.server.address().port}`;
  assert.equal((await fetch(`${base}/`)).status, 403);
  const html = await fetch(`${base}/?token=secret-token`);
  assert.equal(html.status, 200);
  const cookie = html.headers.get("set-cookie");
  assert.match(cookie, /HttpOnly/);
  assert.match(cookie, /SameSite=Strict/);
  assert.equal((await fetch(`${base}/app.js`)).status, 403);
  assert.equal((await fetch(`${base}/app.js`, { headers: { cookie } })).status, 200);
  assert.equal((await fetch(`${base}/app.js`, { headers: { cookie: "rich_md_token=%E0%A4%A" } })).status, 403);
  assert.equal((await fetch(`${base}/api/document`)).status, 403);
  const payload = await (await fetch(`${base}/api/document`, { headers: { authorization: "Bearer secret-token" } })).json();
  assert.equal(payload.absolutePath, await realpath(file));
  const malformed = await fetch(`${base}/api/document`, {
    method: "PUT",
    headers: { authorization: "Bearer secret-token", "content-type": "application/json" },
    body: "{not-json"
  });
  assert.equal(malformed.status, 400);
  assert.equal((await malformed.json()).error, "Malformed JSON");
  await new Promise((resolve) => app.server.close(resolve));
  await rm(root, { recursive: true });
});

test("confines paths and resolves in-repo symlinks safely", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "rich-md-path-"));
  const outside = await mkdtemp(path.join(tmpdir(), "rich-md-outside-"));
  await writeFile(path.join(root, "ok.md"), "# ok\n");
  await writeFile(path.join(outside, "secret.md"), "secret\n");
  await symlink(path.join(root, "ok.md"), path.join(root, "inside.md"));
  await symlink(path.join(outside, "secret.md"), path.join(root, "outside.md"));
  assert.equal((await resolveMarkdown(root, "inside.md")).target, await realpath(path.join(root, "ok.md")));
  await assert.rejects(resolveMarkdown(root, "outside.md"), /escapes repository/);
  await assert.rejects(resolveMarkdown(root, "../" + path.basename(outside) + "/secret.md"), /escapes repository/);
  await rm(root, { recursive: true }); await rm(outside, { recursive: true });
});

test("revision conflict protects external changes", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "rich-md-conflict-"));
  const file = path.join(root, "doc.md");
  await writeFile(file, "one\n");
  const old = await readDocument(file);
  await writeFile(file, "external\n");
  await assert.rejects(atomicSave(file, "mine\n", old.revision), (error) => error.status === 409);
  assert.equal(await readFile(file, "utf8"), "external\n");
  await rm(root, { recursive: true });
});

test("atomic save preserves mode and replaces inode", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "rich-md-atomic-"));
  const file = path.join(root, "doc.md");
  await writeFile(file, "before\n"); await chmod(file, 0o640);
  const before = await stat(file);
  const revision = (await readDocument(file)).revision;
  await atomicSave(file, "after\n", revision);
  const after = await stat(file);
  assert.equal(after.mode & 0o777, 0o640);
  assert.notEqual(after.ino, before.ino);
  assert.equal(await readFile(file, "utf8"), "after\n");
  assert.deepEqual((await readFile(root, { encoding: "utf8" }).catch(() => "")), "");
  await rm(root, { recursive: true });
});

test("ordinary research markdown round-trips representative constructs", () => {
  const markdown = `# Hook research

## Pattern

- Fast opener
- **Visible** payoff with *proof*

1. First beat
2. Second beat

> Keep the claim specific.

Use [source](https://example.com?q=1) and \`inline code\`.

\`\`\`js
const hook = "show, don't tell";
\`\`\`
`;
  const turndown = new TurndownService({ headingStyle: "atx", bulletListMarker: "-", codeBlockStyle: "fenced", emDelimiter: "*" });
  const result = turndown.turndown(marked.parse(markdown));
  assert.match(result, /^# Hook research/m);
  assert.match(result, /\[source\]\(https:\/\/example.com\?q=1\)/);
  assert.match(result, /```js\nconst hook/);
  assert.deepEqual(unsupportedMarkdown(markdown), []);
  assert.deepEqual(unsupportedMarkdown("---\ntitle: x\n---\n| A |\n| - |\n| x |\n<div>x</div>"), ["frontmatter", "HTML", "tables"]);
  assert.deepEqual(unsupportedMarkdown("Text with <span>raw</span>, $x^2$, and [[Wiki]]."), ["HTML", "math", "wiki links"]);
  assert.deepEqual(unsupportedMarkdown("A [normal link](https://example.com).\n\n```\n<div>inside code is text</div>\n```\n"), []);
});

test("launcher reuses the healthy server for the same exact file", { timeout: 30000 }, async () => {
  const fixture = path.join(repo, ".rich-md-launcher-test.md");
  const stateRoot = await mkdtemp(path.join(tmpdir(), "rich-md-launcher-"));
  await writeFile(fixture, "# launcher\n");
  const env = { ...process.env, TMPDIR: stateRoot, RICH_MD_NO_OPEN: "1" };
  const launcher = path.join(repo, "scripts/rich-md");
  await Promise.all([
    execFileAsync(process.execPath, [launcher, fixture], { cwd: repo, env }),
    execFileAsync(process.execPath, [launcher, fixture], { cwd: repo, env })
  ]);
  const key = createHash("sha256").update(repo).digest("hex").slice(0, 16);
  const metadata = path.join(stateRoot, "excerlock-rich-md", `${key}.json`);
  const first = JSON.parse(readFileSync(metadata, "utf8"));
  const starts = readFileSync(path.join(stateRoot, "excerlock-rich-md", `${key}.log`), "utf8")
    .split("\n").filter((line) => {
      try { return JSON.parse(line).file === fixture; } catch { return false; }
    });
  assert.equal(starts.length, 1);
  execFileSync(process.execPath, [launcher, fixture], { cwd: repo, env, stdio: "pipe" });
  const second = JSON.parse(readFileSync(metadata, "utf8"));
  assert.equal(second.pid, first.pid);
  process.kill(first.pid, "SIGTERM");
  await rm(fixture); await rm(stateRoot, { recursive: true, force: true });
});
