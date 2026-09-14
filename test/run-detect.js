#!/usr/bin/env node
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
const start = html.indexOf("function medianInPlace(arr)");
const end = html.indexOf("function workerSource()");
const lerpStart = html.indexOf("function lerp(a, b, t)");
const lerpEnd = html.indexOf("const dpr =");
if (start < 0 || end < 0 || end <= start || lerpStart < 0 || lerpEnd <= lerpStart) {
  console.error("could not extract detector from index.html");
  process.exit(1);
}
const ctx = {
  console,
  Math,
  Uint8Array,
  Uint8ClampedArray,
  Float32Array,
  Int32Array,
  Uint32Array,
  Infinity
};
vm.createContext(ctx);
vm.runInContext(html.slice(lerpStart, lerpEnd) + "\n" + html.slice(start, end), ctx);
const { runDetect } = ctx;

const W = 640, H = 480;
const rgba = new Uint8ClampedArray(W * H * 4);
const dilated = new Uint8Array(W * H);
for (let y = 0; y < H; y++) {
  for (let x = 0; x < W; x++) {
    const i = (y * W + x) * 4;
    rgba[i] = 70; rgba[i + 1] = 55; rgba[i + 2] = 40; rgba[i + 3] = 255;
  }
}
function flash(cx, cy, r) {
  for (let y = cy - r; y <= cy + r; y++) {
    for (let x = cx - r; x <= cx + r; x++) {
      if ((x - cx) ** 2 + (y - cy) ** 2 > r * r) continue;
      const i = (y * W + x) * 4;
      rgba[i] = 255; rgba[i + 1] = 255; rgba[i + 2] = 252;
    }
  }
}
flash(160, 140, 3);
flash(310, 200, 4);
// gold-ish blob should fail whiteness
for (let y = 50; y <= 56; y++) for (let x = 20; x <= 26; x++) {
  const i = (y * W + x) * 4;
  rgba[i] = 220; rgba[i + 1] = 170; rgba[i + 2] = 40;
}
// ROI covers first flash only
for (let y = 110; y < 180; y++) for (let x = 130; x < 190; x++) dilated[y * W + x] = 1;

const params = {
  tPeak: 28, minBright: 205, tTop: 20, tSat: 40, tIsol: 12,
  longEdge: Math.max(W, H), intensity: 0.25
};
const res = runDetect(rgba, W, H, dilated, params, null);
const inRoi = [];
const outRoi = [];
for (let i = 0; i < W * H; i++) {
  if (!res.mask[i]) continue;
  (dilated[i] ? inRoi : outRoi).push(i);
}
console.log(JSON.stringify({ count: res.count, inRoi: inRoi.length, outRoi: outRoi.length }));
if (res.count < 1) {
  console.error("expected at least one flash inside ROI");
  process.exit(1);
}
if (outRoi.length) {
  console.error("yellow leaked outside ROI");
  process.exit(1);
}
const hitOutside = res.mask[200 * W + 310];
if (hitOutside) {
  console.error("detected flash outside painted ROI");
  process.exit(1);
}
console.log("ok");
