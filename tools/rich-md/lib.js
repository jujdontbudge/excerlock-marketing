import { createHash, randomBytes } from "node:crypto";
import { lstat, open, readFile, realpath, rename, stat, unlink, writeFile } from "node:fs/promises";
import path from "node:path";

export const sha256 = (text) => createHash("sha256").update(text).digest("hex");
export const newToken = () => randomBytes(32).toString("base64url");

export async function resolveMarkdown(repo, requested) {
  const root = await realpath(repo);
  const candidate = path.resolve(root, requested);
  let target;
  try {
    target = await realpath(candidate);
  } catch {
    throw Object.assign(new Error("File does not exist"), { status: 404 });
  }
  if (target !== root && !target.startsWith(root + path.sep))
    throw Object.assign(new Error("File escapes repository"), { status: 403 });
  if (path.extname(target).toLowerCase() !== ".md")
    throw Object.assign(new Error("Only .md files are allowed"), { status: 400 });
  const info = await stat(target);
  if (!info.isFile())
    throw Object.assign(new Error("A regular file is required"), { status: 400 });
  return { root, target, relative: path.relative(root, target) };
}

export function unsupportedMarkdown(text) {
  const reasons = [];
  const inspect = text
    .replace(/^ {0,3}(`{3,}|~{3,})[^\n]*\n[\s\S]*?^ {0,3}\1\s*$/gm, "")
    .replace(/(`+)(?:[^`\n]|`(?!\1))*\1/g, "");
  if (/^---\s*\n[\s\S]*?\n---\s*(?:\n|$)/.test(text)) reasons.push("frontmatter");
  if (/<!--[\s\S]*?-->|<\/?[A-Za-z][^>\n]*>|<![A-Z][^>]*>/i.test(inspect)) reasons.push("HTML");
  if (/^\s*\|.*\|\s*\n\s*\|(?:\s*:?-+:?\s*\|)+/m.test(inspect)) reasons.push("tables");
  if (/^\s*\[[^\]]+\]:\s+\S+/m.test(inspect)) reasons.push("reference links");
  if (/^\s*:::+/m.test(inspect)) reasons.push("directives");
  if (/^\s*[-*+]\s+\[[ xX]\]\s+/m.test(inspect)) reasons.push("task lists");
  if (/!\[[^\]]*\]\([^)]+\)/.test(inspect)) reasons.push("images");
  if (/\[\^[^\]]+\]/.test(inspect)) reasons.push("footnotes");
  if (/^\s*\$\$\s*$|(?<!\\)\${1,2}[^$\n]+\${1,2}/m.test(inspect)) reasons.push("math");
  if (/\{\{[\s\S]*?\}\}|\{%[\s\S]*?%\}/.test(inspect)) reasons.push("templates");
  if (/\[\[[^\]\n]+\]\]/.test(inspect)) reasons.push("wiki links");
  if (/^={3,}\s*$|^<{7}(?:\s.*)?$|^>{7}(?:\s.*)?$/m.test(inspect)) reasons.push("merge markers");
  if (/^ {0,3}(?:\+{3}|\-{3})\s+\S.*\n(?:(?!\n\n)[\s\S])*$/.test(inspect) && !reasons.includes("frontmatter"))
    reasons.push("metadata block");
  return reasons;
}

export async function readDocument(target) {
  const content = await readFile(target, "utf8");
  const info = await stat(target);
  return { content, revision: sha256(content), mode: info.mode & 0o777 };
}

export async function atomicSave(target, content, expectedRevision) {
  const current = await readDocument(target);
  if (current.revision !== expectedRevision)
    throw Object.assign(new Error("File changed on disk"), { status: 409, current });
  const dir = path.dirname(target);
  const temp = path.join(dir, `.${path.basename(target)}.rich-md-${process.pid}-${randomBytes(6).toString("hex")}`);
  try {
    await writeFile(temp, content, { mode: current.mode, flag: "wx" });
    const handle = await open(temp, "r");
    try {
      await handle.sync();
    } finally {
      await handle.close();
    }
    const immediatelyBeforeRename = await readDocument(target);
    if (immediatelyBeforeRename.revision !== expectedRevision)
      throw Object.assign(new Error("File changed while saving"), { status: 409, current: immediatelyBeforeRename });
    await rename(temp, target);
    const directory = await open(dir, "r");
    try {
      await directory.sync().catch(() => {});
    } finally {
      await directory.close();
    }
  } catch (error) {
    await unlink(temp).catch(() => {});
    throw error;
  }
  return { revision: sha256(content) };
}
