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
const ctx = {
  console, Math, Uint8Array, Uint8ClampedArray, Float32Array, Int32Array, Uint32Array, Infinity
};
vm.createContext(ctx);
vm.runInContext(html.slice(lerpStart, lerpEnd) + "\n" + html.slice(start, end), ctx);
const { runDetect, lerp } = ctx;

function loadRgba(file) {
  const buf = fs.readFileSync(file);
  const w = buf.readUInt32LE(0);
  const h = buf.readUInt32LE(4);
  return { w, h, rgba: new Uint8ClampedArray(buf.buffer, buf.byteOffset + 8, w * h * 4) };
}

function paramsFor(w, h, i) {
  return {
    tPeak: lerp(26, 12, i),
    minBright: lerp(214, 165, i),
    tTop: lerp(18, 9, i),
    tSat: lerp(40, 60, i),
    tIsol: lerp(12, 6, i),
    longEdge: Math.max(w, h),
    intensity: i
  };
}

function roiRect(w, h, x0, y0, x1, y1) {
  const m = new Uint8Array(w * h);
  for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) m[y * w + x] = 1;
  return m;
}

function run(name, file, rect, intensities) {
  const { w, h, rgba } = loadRgba(file);
  const dilated = roiRect(w, h, ...rect);
  const out = { name, w, h, rect };
  for (const i of intensities) {
    const t0 = Date.now();
    const res = runDetect(rgba, w, h, dilated, paramsFor(w, h, i), null);
    let pix = 0;
    for (let k = 0; k < res.mask.length; k++) if (res.mask[k]) pix++;
    out["i" + i] = { count: res.count, pix, ms: Date.now() - t0 };
  }
  console.log(JSON.stringify(out));
}

const dir = path.join(__dirname, "examples");
const I = [0, 0.25, 0.5, 1];
// 01: dark paint sky (upper canvas), tablecloth, full frame
run("01-dark-sky", path.join(dir, "01-overzicht.rgba"), [80, 40, 980, 220], I);
run("01-tablecloth", path.join(dir, "01-overzicht.rgba"), [430, 430, 720, 620], I);
run("01-halo-jesus", path.join(dir, "01-overzicht.rgba"), [430, 80, 620, 280], I);
// 02: dark bg, plate metal
run("02-dark-bg", path.join(dir, "02-dienaar.rgba"), [40, 20, 520, 220], I);
run("02-plate", path.join(dir, "02-dienaar.rgba"), [40, 380, 520, 560], I);
run("02-full", path.join(dir, "02-dienaar.rgba"), [0, 0, 1023, 681], I);
// 03: dark wall right, halo, studio wall top
run("03-dark-wall", path.join(dir, "03-emmaus.rgba"), [520, 40, 980, 280], I);
run("03-halo", path.join(dir, "03-emmaus.rgba"), [40, 80, 360, 420], I);
