import { readFileSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// Read only the dedicated user-owned file; never execute shell/dotenv content.
const root = join(homedir(), "excerlockmarketing");
const allowed = new Set(["JINA_API_KEY", "YOUTUBE_API_KEY", "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT", "META_ACCESS_TOKEN", "TIKTOK_ACCESS_TOKEN", "TIKTOK_MS_TOKEN", "FAL_KEY", "MEM0_TELEMETRY"]);
export default function (pi: ExtensionAPI) {
  const path = join(root, ".env");
  if (existsSync(path)) {
    for (const line of readFileSync(path, "utf8").split(/\r?\n/)) {
      const match = /^([A-Z][A-Z0-9_]*)=(.*)$/.exec(line.trim());
      if (!match || !allowed.has(match[1])) continue;
      let value = match[2].trim();
      if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) value = value.slice(1, -1);
      if (value && !process.env[match[1]]) process.env[match[1]] = value;
    }
  }
  process.env.MEM0_TELEMETRY ??= "0";
  const statusCommand: Parameters<ExtensionAPI["registerCommand"]>[1] = {
    description: "ExcerLock marketing workspace and credential presence (never key values)",
    handler: async (_args, ctx) => {
      const keys = [...allowed].filter(k => /KEY|TOKEN|CLIENT_ID|CLIENT_SECRET/.test(k));
      ctx.ui.notify(`${root}/README.md\n${keys.map(k => `${k}: ${process.env[k] ? "set (not verified)" : "missing"}`).join("\n")}\nImage gen = Codex plugin only; fal = Seedance video only.`, "info");
    },
  };
  pi.registerCommand("marketing-status", statusCommand);
}
