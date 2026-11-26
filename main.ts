// news-image-20261126 — entry program.
//
// The repository holds one composed front page, entry.png, which sums up the
// world's news of Thursday 26 November 2026. This program validates the
// image against the competition gate's limits and copies it to the output
// directory the grader points at (/output, or $MAKEFUN_OUTPUT_DIR locally).
// Node 22, standard library only, no network. Deterministic: the same input
// file always produces the same output bytes.

import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1_048_576; // 1 MiB
const MAX_SIDE = 1024;

function pngSize(buf) {
  // PNG: 8-byte signature, then IHDR with width/height as big-endian uint32.
  if (buf.length < 24) return null;
  const sig = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
  for (let i = 0; i < sig.length; i++) if (buf[i] !== sig[i]) return null;
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20), kind: "png" };
}

function jpegSize(buf) {
  // JPEG: walk the segments until a start-of-frame marker carries the size.
  if (buf.length < 4 || buf[0] !== 0xff || buf[1] !== 0xd8) return null;
  let off = 2;
  while (off + 9 < buf.length) {
    if (buf[off] !== 0xff) return null;
    const marker = buf[off + 1];
    if (marker >= 0xc0 && marker <= 0xcf && marker !== 0xc4 && marker !== 0xc8 && marker !== 0xcc) {
      return { height: buf.readUInt16BE(off + 5), width: buf.readUInt16BE(off + 7), kind: "jpeg" };
    }
    off += 2 + buf.readUInt16BE(off + 2);
  }
  return null;
}

function main() {
  const here = dirname(fileURLToPath(import.meta.url));
  const source = join(here, "entry.png");
  if (!existsSync(source)) throw new Error("entry.png is missing beside main.ts");

  const bytes = readFileSync(source);
  if (bytes.length > MAX_BYTES) throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
  const size = pngSize(bytes) ?? jpegSize(bytes);
  if (!size) throw new Error("entry.png is neither a whole PNG nor a whole JPEG");
  if (size.width > MAX_SIDE || size.height > MAX_SIDE) {
    throw new Error(`entry.png is ${size.width}x${size.height}, over the 1024x1024 limit`);
  }

  const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
  mkdirSync(outDir, { recursive: true });
  copyFileSync(source, join(outDir, "entry.png"));
  console.log(`entry.png: ${size.kind} ${size.width}x${size.height}, ${bytes.length} bytes -> ${outDir}/entry.png`);
}

main();
