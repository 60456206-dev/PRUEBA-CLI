#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { bundle } from "@remotion/bundler";
import { openBrowser, renderMedia, selectComposition } from "@remotion/renderer";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SRC_DIR = path.join(__dirname, "src");
const PUBLIC_DIR = path.join(__dirname, "public");
const BUNDLE_ROOT = path.join(__dirname, ".remotion_bundle");
const BUNDLE_OUT = path.join(BUNDLE_ROOT, "bundle");
const MANIFEST_PATH = path.join(BUNDLE_ROOT, "manifest.json");

function collectFiles(dir) {
  if (!fs.existsSync(dir)) return [];
  const entries = fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name));
  const files = [];
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...collectFiles(full));
    } else if (entry.isFile()) {
      files.push(full);
    }
  }
  return files;
}

function computeSourceHash() {
  const hash = crypto.createHash("sha256");
  const extra = [path.join(__dirname, "package.json")];
  const allFiles = [...collectFiles(SRC_DIR), ...collectFiles(PUBLIC_DIR), ...extra.filter((f) => fs.existsSync(f))];
  for (const filePath of allFiles) {
    hash.update(path.relative(__dirname, filePath));
    hash.update(fs.readFileSync(filePath));
  }
  return hash.digest("hex");
}

async function ensureCachedBundle() {
  const sourceHash = computeSourceHash();
  if (
    fs.existsSync(MANIFEST_PATH) &&
    fs.existsSync(path.join(BUNDLE_OUT, "index.html"))
  ) {
    try {
      const prev = JSON.parse(fs.readFileSync(MANIFEST_PATH, "utf8"));
      if (prev.hash === sourceHash) {
        return { serveUrl: BUNDLE_OUT, reused: true };
      }
    } catch {
      // Rebuild if manifest is corrupt
    }
  }

  fs.rmSync(BUNDLE_OUT, { recursive: true, force: true });
  fs.mkdirSync(BUNDLE_ROOT, { recursive: true });
  const serveUrl = await bundle({
    entryPoint: path.join(SRC_DIR, "index.ts"),
    outDir: BUNDLE_OUT,
    publicDir: fs.existsSync(PUBLIC_DIR) ? PUBLIC_DIR : undefined,
  });
  fs.writeFileSync(MANIFEST_PATH, JSON.stringify({ hash: sourceHash, updatedAt: new Date().toISOString() }, null, 2));
  return { serveUrl, reused: false };
}

async function main() {
  const batchJsonPath = process.argv[2];
  if (!batchJsonPath || !fs.existsSync(batchJsonPath)) {
    console.error("Uso: node render_batch.mjs <batch_jobs.json>");
    process.exit(2);
  }

  const payload = JSON.parse(fs.readFileSync(batchJsonPath, "utf8"));
  const jobs = Array.isArray(payload.jobs) ? payload.jobs : [];
  if (jobs.length === 0) {
    console.log("[REMOTION-BATCH] Sin trabajos que renderizar.");
    return;
  }

  const { serveUrl, reused } = await ensureCachedBundle();
  console.log(`[REMOTION-BATCH] Bundle ${reused ? "reutilizado desde caché" : "compilado"} -> ${serveUrl}`);

  const gl = payload.gl || "angle";
  const defaultConcurrency = Number(payload.concurrency || 2);
  const browser = await openBrowser("chrome", {
    chromiumOptions: { gl },
  });

  try {
    for (const job of jobs) {
      const compId = job.compositionId;
      const outPath = job.outputLocation;
      const inputProps = job.inputProps || {};
      const transparent = Boolean(job.transparent);
      const codec = transparent ? "vp8" : (job.codec || "h264");
      const crf = transparent ? undefined : Number(job.crf ?? 14);
      const concurrency = Number(job.concurrency || defaultConcurrency);

      fs.mkdirSync(path.dirname(outPath), { recursive: true });
      const composition = await selectComposition({
        serveUrl,
        id: compId,
        inputProps,
        puppeteerInstance: browser,
        chromiumOptions: { gl },
      });

      await renderMedia({
        composition,
        serveUrl,
        codec,
        outputLocation: outPath,
        inputProps,
        puppeteerInstance: browser,
        chromiumOptions: { gl },
        concurrency,
        ...(transparent ? { imageFormat: "png", pixelFormat: "yuva420p" } : { pixelFormat: "yuv420p" }),
        ...(crf !== undefined ? { crf } : {}),
        overwrite: true,
        logLevel: "error",
      });
      const kb = (fs.statSync(outPath).size / 1024).toFixed(1);
      console.log(`[REMOTION-BATCH] ✅ ${path.basename(outPath)} (${compId}, ${kb} KB)`);
    }
  } finally {
    await browser.close({ silent: true });
  }
}

main().catch((err) => {
  console.error("[REMOTION-BATCH] ❌ Error fatal:", err);
  process.exit(1);
});
