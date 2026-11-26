// Entry point for the news-image-20261126 bounty.
//
// Reads entry.png next to this script, validates it against the bounty
// limits (a whole PNG or JPEG, at most 1 MiB, at most 1024x1024), then
// copies it to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png when
// the variable is unset) and reports what it did.
//
// Node 22, standard library only. No network access.

import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1_048_576;
const MAX_SIDE = 1024;

const here = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(here, "entry.png");

function fail(message) {
  console.error(`error: ${message}`);
  process.exit(1);
}

// --- PNG / JPEG size parsing (no dependencies) ---------------------------

function pngSize(buf) {
  // PNG signature, then the IHDR chunk: width and height are the first
  // two big-endian uint32 values after the 8-byte chunk header.
  const signature = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
  for (let i = 0; i < signature.length; i++) {
    if (buf[i] !== signature[i]) return null;
  }
  if (buf.toString("ascii", 12, 16) !== "IHDR") return null;
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}

function jpegSize(buf) {
  // Walk the marker segments until a start-of-frame marker gives the
  // dimensions (height first, then width, both big-endian uint16).
  if (buf[0] !== 0xff || buf[1] !== 0xd8) return null;
  let pos = 2;
  while (pos + 9 < buf.length) {
    if (buf[pos] !== 0xff) return null;
    const marker = buf[pos + 1];
    if (marker >= 0xc0 && marker <= 0xcf && marker !== 0xc4 && marker !== 0xc8 && marker !== 0xcc) {
      return { width: buf.readUInt16BE(pos + 7), height: buf.readUInt16BE(pos + 5) };
    }
    const segmentLength = buf.readUInt16BE(pos + 2);
    pos += 2 + segmentLength;
  }
  return null;
}

function imageSize(buf) {
  return pngSize(buf) ?? jpegSize(buf);
}

// --- validate ------------------------------------------------------------

if (!existsSync(sourcePath)) {
  fail(`entry.png not found next to main.ts (${sourcePath})`);
}

const bytes = statSync(sourcePath).size;
if (bytes > MAX_BYTES) {
  fail(`entry.png is ${bytes} bytes, over the 1 MiB limit`);
}

const data = readFileSync(sourcePath);
const size = imageSize(data);
if (size === null) {
  fail("entry.png is not a whole PNG or JPEG image");
}
if (size.width > MAX_SIDE || size.height > MAX_SIDE) {
  fail(`entry.png is ${size.width}x${size.height}, over the 1024x1024 limit`);
}

// --- deliver -------------------------------------------------------------

const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const target = resolve(outDir, "entry.png");
mkdirSync(outDir, { recursive: true });
copyFileSync(sourcePath, target);

console.log(
  JSON.stringify({
    status: "ok",
    source: sourcePath,
    output: target,
    bytes,
    width: size.width,
    height: size.height,
  }),
);
