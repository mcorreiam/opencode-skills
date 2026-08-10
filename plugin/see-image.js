import { z } from "zod";
import path from "path";
import os from "os";
import fs from "fs";

const VISION_PROVIDER = process.env.SEE_IMAGE_PROVIDER || "alibaba-token-plan";
const VISION_MODEL = process.env.SEE_IMAGE_MODEL || "qwen3.6-flash";
const VISION_TIMEOUT = Number(process.env.SEE_IMAGE_TIMEOUT) || 30000;

const EXT_MEDIA = {
  png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg",
  gif: "image/gif", webp: "image/webp", bmp: "image/bmp",
};

function modelSupportsVision(model) {
  if (!model) return false;
  if (typeof model.capabilities?.input?.image === "boolean") return model.capabilities.input.image;
  if (Array.isArray(model.modalities?.input)) return model.modalities.input.includes("image");
  if (typeof model.capabilities?.attachment === "boolean") return model.capabilities.attachment;
  if (typeof model.attachment === "boolean") return model.attachment;
  return false;
}

function isImagePart(p) {
  return p?.type === "file" && typeof p.url === "string" && p.url.startsWith("data:")
    && typeof p.mime === "string" && p.mime.startsWith("image/");
}

function normalizeName(name) {
  return path.basename(name.trim()).normalize("NFKC").replace(/[\u202f\u00a0]/g, " ").replace(/\s+/g, " ").toLowerCase();
}

function pickImage(parts, name) {
  if (!name || name === "clipboard" || name === "latest")
    return parts.length ? parts[parts.length - 1] : null;
  for (let i = parts.length - 1; i >= 0; i--)
    if (parts[i].filename === name) return parts[i];
  const want = normalizeName(name);
  for (let i = parts.length - 1; i >= 0; i--)
    if (parts[i].filename && normalizeName(parts[i].filename) === want) return parts[i];
  return null;
}

async function getSessionImages(client, sessionID) {
  try {
    const res = await client.session.messages({ path: { id: sessionID } });
    const parts = [];
    for (const msg of res?.data ?? [])
      for (const part of msg?.parts ?? [])
        if (isImagePart(part)) parts.push(part);
    return parts;
  } catch { return []; }
}

function resolveFromFileSystem(name, cwd) {
  if (name.startsWith("~")) name = path.join(os.homedir(), name.slice(1));
  let abs = null;
  if (path.isAbsolute(name) && fs.existsSync(name)) abs = name;
  else if (fs.existsSync(path.resolve(cwd, name))) abs = path.resolve(cwd, name);
  if (!abs) {
    const home = os.homedir();
    const dirs = ["/tmp", path.join(home, "Pictures", "Screenshots"), path.join(home, "Pictures"),
                  path.join(home, "Desktop"), path.join(home, "Downloads"), cwd];
    for (const dir of dirs)
      if (fs.existsSync(path.join(dir, name))) { abs = path.join(dir, name); break; }
  }
  if (!abs) return null;
  const ext = path.extname(abs).slice(1).toLowerCase();
  const mediaType = EXT_MEDIA[ext] || "image/png";
  const b64 = Buffer.from(fs.readFileSync(abs)).toString("base64");
  return { dataUrl: `data:${mediaType};base64,${b64}`, mediaType, source: abs };
}

async function resolveImage(name, cwd, sessionID, client) {
  const wantLatest = !name || name === "clipboard" || name === "latest";

  if (client && sessionID) {
    const parts = await getSessionImages(client, sessionID);
    const hit = pickImage(parts, name);
    if (hit) return { dataUrl: hit.url, mediaType: hit.mime || "image/png", source: "opencode-session" };
  }
  if (!wantLatest) {
    const fromFs = resolveFromFileSystem(name, cwd);
    if (fromFs) return fromFs;
  }
  if (!wantLatest && client && sessionID) {
    const parts = await getSessionImages(client, sessionID);
    const latest = pickImage(parts, "");
    if (latest) return { dataUrl: latest.url, mediaType: latest.mime || "image/png", source: "opencode-session-latest" };
  }

  const known = client && sessionID
    ? [...new Set((await getSessionImages(client, sessionID)).map(p => p.filename).filter(Boolean))].slice(-5)
    : [];
  throw new Error(
    `see_image: could not find "${name || "any attached image"}". ` +
    (known.length
      ? `Images attached: ${known.map(f => `"${f}"`).join(", ")}. Retry with one of those filenames.`
      : `No images found. Ask the user to re-attach or provide a file path.`),
  );
}

async function callVisionModel(client, dataUrl, mediaType, prompt, abort) {
  let sessionID;
  try {
    const sessionRes = await Promise.race([
      client.session.create({ body: {} }),
      new Promise((_, reject) => setTimeout(() => reject(new Error(`timed out after ${VISION_TIMEOUT}ms`)), VISION_TIMEOUT)),
    ]);
    sessionID = sessionRes.data?.id;
    if (!sessionID) throw new Error("no session ID");

    const controller = new AbortController();
    const onAbort = () => controller.abort();
    abort?.addEventListener("abort", onAbort);
    const timer = setTimeout(() => controller.abort(), VISION_TIMEOUT);
    try {
      const res = await client.session.prompt({
        path: { id: sessionID },
        body: {
          model: { providerID: VISION_PROVIDER, modelID: VISION_MODEL },
          parts: [
            { type: "file", mime: mediaType, url: dataUrl },
            { type: "text", text: prompt },
          ],
          tools: {},
          system: "You are a vision assistant. Describe the image accurately and concisely. Answer with text only.",
        },
        signal: controller.signal,
      });
      const text = (res.data?.parts ?? [])
        .filter(p => p.type === "text").map(p => p.text)
        .filter(t => typeof t === "string" && t.length > 0)
        .join("\n").trim();
      if (!text) throw new Error("no text in response");
      return text;
    } finally {
      clearTimeout(timer);
      abort?.removeEventListener("abort", onAbort);
    }
  } finally {
    if (sessionID) await client.session.delete({ path: { id: sessionID } }).catch(() => {});
  }
}

const SYSTEM_INSTRUCTIONS = `# See Image (vision bridge)

You have a \`see_image\` tool. When the user attaches an image, this model cannot view it directly. You MUST call \`see_image\` — do NOT tell the user you can't see images.

## When to call \`see_image\`

Call it immediately when:
1. You receive an error containing \`Cannot read\` or \`this model does not support image input\`
2. The user's message has an image placeholder like \`[Image #1]\`
3. The user references an image/screenshot (".png", ".jpg", "see this")

## How to use it

1. Pass \`filePath\` if you know the filename (e.g. from an error message)
2. Omit \`filePath\` to use the most recent attached image
3. Pass \`question\` for a specific query, or omit for a full description
4. Answer using the returned description as if you saw the image

## Rules

- NEVER just repeat the error to the user. Call the tool.
- Do NOT use \`see_image\` for text files — use \`read\` instead.
- Never guess image contents.`;

const SeeImagePlugin = async (ctx) => {
  const { client } = ctx;

  const seeImageTool = {
    description: 'See an image/screenshot the current model cannot view. Use when you get a "this model does not support image input" / "Cannot read" error, when the message contains [Image #1], or when an image is referenced. Routes the image to a vision-capable model and returns a textual description.',
    args: {
      filePath: z.string().optional().describe('Path to the image, or omit to use the most recent attached image.'),
      question: z.string().optional().describe('Specific question about the image. Omit for a full description.'),
    },
    async execute(args, context) {
      const resolved = await resolveImage(args.filePath || "", context.directory, context.sessionID, client);

      const prompt = args.question?.trim()
        ? args.question
        : "Describe this image in detail. If it is a screenshot, describe the UI, text content, and layout precisely.";

      context.metadata({ title: "see_image: looking…", metadata: { working: true } });
      const result = await callVisionModel(client, resolved.dataUrl, resolved.mediaType, prompt, context.abort);
      context.metadata({ title: "see_image: done", metadata: { model: VISION_MODEL, provider: VISION_PROVIDER, source: resolved.source } });

      return result;
    },
  };

  return {
    tool: { see_image: seeImageTool },
    "experimental.chat.system.transform": async (input, output) => {
      if (modelSupportsVision(input.model)) return;
      output.system.push(SYSTEM_INSTRUCTIONS);
    },
  };
};

export default SeeImagePlugin;
