#!/usr/bin/env node
import http from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { atomicSave, newToken, readDocument, resolveMarkdown, unsupportedMarkdown } from "./lib.js";

const here = path.dirname(fileURLToPath(import.meta.url));

function json(response, status, value) {
  response.writeHead(status, { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" });
  response.end(JSON.stringify(value));
}

function hasBrowserToken(request, token) {
  try {
    const cookies = Object.fromEntries((request.headers.cookie || "").split(";").map((part) => {
      const at = part.indexOf("=");
      return at < 0 ? ["", ""] : [part.slice(0, at).trim(), decodeURIComponent(part.slice(at + 1))];
    }));
    return cookies.rich_md_token === token;
  } catch {
    return false;
  }
}

async function body(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > 10 * 1024 * 1024) throw Object.assign(new Error("Request too large"), { status: 413 });
    chunks.push(chunk);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf8"));
  } catch {
    throw Object.assign(new Error("Malformed JSON"), { status: 400 });
  }
}

export async function createRichMdServer({ repo, file, token = newToken(), dist = path.join(here, "dist") }) {
  const selected = await resolveMarkdown(repo, file);
  const server = http.createServer(async (request, response) => {
    try {
      const url = new URL(request.url, "http://127.0.0.1");
      if (url.pathname === "/health") {
        if (url.searchParams.get("token") !== token) return json(response, 403, { error: "Forbidden" });
        return json(response, 200, { pid: process.pid, file: selected.target, identity: "excerlock-rich-md-v1" });
      }
      if (url.pathname.startsWith("/api/")) {
        if (request.headers.authorization !== `Bearer ${token}`) return json(response, 403, { error: "Forbidden" });
        if (url.pathname === "/api/document" && request.method === "GET") {
          const document = await readDocument(selected.target);
          return json(response, 200, {
            ...document,
            title: path.basename(selected.target, ".md"),
            path: selected.relative,
            absolutePath: selected.target,
            unsupported: unsupportedMarkdown(document.content)
          });
        }
        if (url.pathname === "/api/document" && request.method === "PUT") {
          const value = await body(request);
          if (typeof value.content !== "string" || typeof value.revision !== "string")
            return json(response, 400, { error: "Invalid document" });
          const unsupported = unsupportedMarkdown(value.content);
          if (unsupported.length) return json(response, 422, { error: `Unsupported Markdown: ${unsupported.join(", ")}` });
          return json(response, 200, await atomicSave(selected.target, value.content, value.revision));
        }
        return json(response, 404, { error: "Not found" });
      }
      const queryToken = url.searchParams.get("token");
      const validQuery = url.pathname === "/" && queryToken === token;
      if (!validQuery && !hasBrowserToken(request, token))
        return json(response, 403, { error: "Forbidden" });
      const asset = url.pathname === "/" ? "index.html" : url.pathname.slice(1);
      const full = path.resolve(dist, asset);
      if (full !== dist && !full.startsWith(dist + path.sep)) return json(response, 403, { error: "Forbidden" });
      const data = await readFile(full);
      const types = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css" };
      const headers = { "content-type": types[path.extname(full)] || "application/octet-stream" };
      if (validQuery) headers["set-cookie"] = `rich_md_token=${encodeURIComponent(token)}; HttpOnly; SameSite=Strict; Path=/`;
      response.writeHead(200, headers);
      response.end(data);
    } catch (error) {
      if (error.status === 409) return json(response, 409, { error: error.message, currentRevision: error.current.revision });
      json(response, error.status || 500, { error: error.message });
    }
  });
  return { server, selected, token };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [repo, file, token] = process.argv.slice(2);
  if (!repo || !file || !token) throw new Error("usage: server.js REPO FILE TOKEN");
  const app = await createRichMdServer({ repo, file, token });
  app.server.listen(0, "127.0.0.1", () => {
    const address = app.server.address();
    process.stdout.write(`${JSON.stringify({ port: address.port, pid: process.pid, file: app.selected.target })}\n`);
  });
}
