import { readFile } from "node:fs/promises";
import { extname } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

const CODEX_IMAGE = process.env.CODEX_IMAGE_BIN || "/Users/johansardar/.local/bin/codex-image";
const MAX_PREVIEW_BYTES = 20 * 1024 * 1024;
const TIMEOUT_MS = 15 * 60 * 1000;

type ImageRequest = { prompt: string; images?: string[]; edit?: boolean; output?: string };
type ImageResult = { ok: boolean; path: string; source_path?: string; mode?: string };
type ResultContent = Array<{ type: "text"; text: string } | { type: "image"; data: string; mimeType: string }>;

function mimeType(path: string): string | undefined {
  switch (extname(path).toLowerCase()) {
    case ".png": return "image/png";
    case ".jpg":
    case ".jpeg": return "image/jpeg";
    case ".webp": return "image/webp";
  }
}

async function runBridge(pi: ExtensionAPI, request: ImageRequest, cwd: string, signal?: AbortSignal): Promise<ImageResult> {
  const args = ["--json", "--cwd", cwd];
  for (const image of request.images ?? []) args.push("--image", image);
  if (request.edit) args.push("--edit");
  if (request.output) args.push("--output", request.output);
  args.push("--", request.prompt);

  const result = await pi.exec(CODEX_IMAGE, args, { cwd, signal, timeout: TIMEOUT_MS });
  if (result.code !== 0) {
    throw new Error((result.stderr || result.stdout || `codex-image exited ${result.code}`).trim().slice(-4000));
  }
  let value: ImageResult;
  try {
    value = JSON.parse(result.stdout);
  } catch {
    throw new Error(`codex-image returned invalid JSON: ${result.stdout.slice(-2000)}`);
  }
  if (!value.ok || !value.path) throw new Error("codex-image did not return an output path");
  return value;
}

async function resultContent(value: ImageResult): Promise<ResultContent> {
  const content: ResultContent = [
    { type: "text", text: `Image ${value.mode === "edit" ? "edited" : "generated"}: ${value.path}` },
  ];
  const mediaType = mimeType(value.path);
  if (mediaType) {
    const image = await readFile(value.path);
    if (image.byteLength <= MAX_PREVIEW_BYTES) {
      content.push({ type: "image", data: image.toString("base64"), mimeType: mediaType });
    }
  }
  return content;
}

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "codex_image",
    label: "Codex Image",
    description: "Generate or edit an image through the locally authenticated Codex image_gen bridge. Accepts an exact final prompt, optional reference images, edit mode, and an optional output path. Existing output files are never overwritten.",
    promptSnippet: "Generate or edit still images with the subscription-backed Codex image bridge",
    promptGuidelines: [
      "Use codex_image only when the user requests actual still-image generation or editing.",
      "For image requests, clarify requirements when needed and prepare a suitable final prompt; once finalized, pass that prompt to codex_image unchanged.",
      "Use codex_image images for local reference files, set edit=true for edits, and provide a project output path when the result should be retained.",
      "Use fal.ai rather than codex_image for video generation.",
    ],
    parameters: Type.Object({
      prompt: Type.String({ minLength: 1, description: "The user's final image prompt, passed unchanged to the bridge" }),
      images: Type.Optional(Type.Array(Type.String({ description: "Readable local reference or edit-target image path" }))),
      edit: Type.Optional(Type.Boolean({ description: "Treat every attached image as an edit target" })),
      output: Type.Optional(Type.String({ description: "New destination path; the tool refuses to overwrite an existing file" })),
    }),
    async execute(_toolCallId, params, signal, onUpdate, ctx) {
      onUpdate?.({ content: [{ type: "text", text: params.edit ? "Editing image with Codex…" : "Generating image with Codex…" }], details: {} });
      const value = await runBridge(pi, params, ctx.cwd, signal);
      return { content: await resultContent(value), details: value };
    },
  });

  pi.registerCommand("image", {
    description: "Start an image workflow using the codex_image tool",
    handler: async (args, ctx) => {
      const request = args.trim();
      const instruction = request
        ? `Use the codex_image tool for this image request. Interpret the request, clarify important missing requirements when necessary, prepare a suitable final prompt, and then generate or edit the image. Do not treat the text below as an exact final prompt unless I explicitly say it is one.\n\nImage request:\n${request}`
        : "Start an image workflow using the codex_image tool. Ask what image I want to generate or edit and gather any important missing requirements before using the tool.";
      await ctx.sendUserMessage(instruction);
    },
  });
}
