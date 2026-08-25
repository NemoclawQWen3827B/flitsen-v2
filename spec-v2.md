# Flits-verwijderaar V2 — product spec (canonical)

Guided, region-first flash restorer. No AI. No stripe retouch. No full-image auto-clean.
Pure JS (canvas + typed arrays), no dependencies. One self-contained HTML file.

## What V2 is (and is not)

V2 is a guided, region-first restorer. The user uploads a painting photo, roughly paints where flash lives, the tool finds only the fiercest white reflections inside that paint, fills those dots locally, then offers a second screen to pick off remaining dots.

It is NOT:
- iPhoto/Photos "retouch" (that smears linear scratches, weave, brushstrokes)
- a full-image auto-clean
- a generative inpaint of whole patches
- an AI advisor

The human decides WHERE detection is allowed. The machine decides which tiny white peaks inside that area look like flash.

Speed comes from not scanning the whole painting (skin, gold, parchment stay out of the detector unless painted in).

## Keep from V1 (hard requirements)
- Worker/background processing for huge photos (detection runs off the main thread; UI stays responsive).
- Zoom/pan on both pages.
- Format-preserving export: PNG stays PNG; JPEG exported at full quality (q=1.0).
- Original bitmap kept in memory for the restore tool.

## V2 process (two pages, not four)

### Page 1 — "Waar zitten de flitsen?"
1. Upload JPEG/PNG. Original bitmap kept in memory (lossless working copy, e.g. ImageData, even for JPEG input).
2. Show the original with zoom/pan (wheel zoom at cursor, drag pan; 100% and fit buttons).
3. User roughly marks regions: wide pink overlay, coarse brush or freehand lasso, multi-region (one or many blobs). Overshooting onto safe paint is OK; undershooting means leftovers on page 2.
4. One simple intensity control: slider/segment "Alleen de felste" (default) <-> "Ook zwakkere witte stippen".
5. User confirms "Detecteer in selectie".
6. Preview ONLY inside the (slightly dilated) pink ROI: yellow dots = what will be removed. Nothing yellow outside the ROI, ever. Run in a Web Worker; show progress.
7. User can grow/shrink the pink and re-run. When yellow looks right: "Invullen" (or "Volgende").

Fill happens only on accepted yellow pixels (incl. small halo), using local median of nearby UNMASKED pixels in a disk slightly larger than the spec. Never a stripe-healer along a stroke, no region-wide inpaint, no diffusion.

Screen copy: "Markeer grof de gebieden met flits. Alleen dáár zoekt de tool de felste witte stippen. Strepen en verfhighlights buiten (en zoveel mogelijk binnen) de markering blijven staan."

### Page 2 — "Nakijken"
Same photo, now the filled result. Before/after toggle (hold to compare or toggle).

Two small tools (the remaining human work):
- "Extra puntje weg" — click or tiny brush on a leftover flash spec: run the detector in a SMALL neighborhood / mini-ROI around the pointer (clipped window), fill if found; if nothing is detected, do nothing (no blind fill).
- "Herstellen" — paint over a wrongly removed highlight: copy those pixels back from the ORIGINAL bitmap + 1px seam blend (feather edges to avoid a hard ring).
- Undo stack (covers fills, page-2 edits, restores).
- Export from this page, original format (PNG->PNG, JPEG->JPEG q=1.0). Download link + format label.

Screen copy: "Controleer het resultaat. Klik of sleep extra flitsstippen weg. Gebruik Herstellen als er per ongeluk een echte highlight is verdwenen."

## Detection scope (architectural change vs V1)

V1: detect everywhere -> user checks yellow overlay on the full painting -> fill -> regional cleanup.
V2: user ROI first -> detect as if the rest of the image did not exist -> fill those specs -> page 2 for misses.

Implementation: run the dual-path detector, but NEVER form candidates outside the ROI (faster, and no accidental yellow on a cheek). The pink ROI mask is dilated a few pixels (e.g. 4-8px, scaled with image size / zoom-independent in image space) so a sloppy outline still catches glow around a boundary spec. Do not dilate so far it eats into unmarked faces.

## Detection (inside ROI only), dual-path OR, then component filters

Pixel-level, luma L = 0.2126R + 0.7152G + 0.0722B.

Path A (white on dark/medium, robust):
- Robust local background B via strided sliding median (window ~2M+1, M ~ longEdge/120, stride ~M; local MAD from the same histogram).
- Candidate where L - B > tPeak AND L > minBright AND tPeak_eff >= max(tPeak, 1.5*MAD).

Path B (top-hat for mid/light paint):
- opened = erode(dilate(L,k)) box, k ~ max(3, longEdge/400); topHat = L - opened.
- Candidate where topHat > tTop.

Whiteness: sat = max(RGB)-min(RGB). Component must be >=75% pixels with sat < tSat, and meanL >= minBright.

Component-level filters (connected components of the candidate set):
- Size: minArea..maxArea; max diameter Dmax = longEdge/lerp(48,34,intensity); min diameter ~ max(2, longEdge/3000).
- Compact: bbox aspect <= 1.7 AND extent = area/bboxArea >= 0.45 (rejects scratches/canvas ribs/fibers). Anti-iPhoto rule: long thin candidates are rejected.
- Isolation/ring test: ring mean (bbox dilated by ringW ~ max(3, longEdge/500), minus the blob) < blob mean - tIsol (rejects broad bright plateaus where the ring is also bright: sheen/highlight, not a spec).
- Peak: blob mean > local background mean + tPeak.

Accept -> halo: dilate accepted pixels by haloR ~ clamp(round(r*0.5)+2, 2, 8) (r = blob radius), clipped to the dilated ROI (never leaves the pink).

Intensity slider mapping (i=0 "felste" .. 1 "meer", default i ~ 0.25):
- tPeak lerp(28,14), minBright lerp(205,160), tTop lerp(20,10), tSat lerp(40,60), tIsol lerp(12,6).
(These are starting defaults; expose NO sliders beyond the single intensity control. Tune if needed after testing.)

## Constraints
- No AI anywhere. No network calls from the page. No dependencies. Single file index.html.
- All UI copy in Dutch (Maartje-shaped, warm, plain).
- Memory: work at full resolution up to ~20MP; if larger, downscale working copy with a clear note (keep export at original resolution via the untouched original bitmap).
- No settings jungle: the ONLY control is the intensity slider + ROI + the two page-2 tools.

## Recreate checklist (V2)
1. Upload -> keep original bitmap.
2. Coarse ROI brush, pink overlay, multi-region.
3. Detector runs only inside (slightly dilated) ROI.
4. Dual-path "white isolated peak", biased to fiercest by default.
5. Reject long/fibrous candidates (anti-iPhoto).
6. Yellow preview inside ROI only -> confirm -> local median fill of those pixels.
7. Page 2: leftovers via click/mini-ROI; restore from original.
8. Export original format.
9. No AI.

## One-sentence V2
The user paints roughly where flash is allowed; the tool removes only the strongest, compact, isolated white peaks inside that paint — never as stroke retouch — then she hunts leftovers on a second page.
