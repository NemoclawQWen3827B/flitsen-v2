# Flitsen V2 — spec (rebuild)

Guided, region-first flash restorer. Two pages. No AI. Pure JS (canvas/typed arrays), no dependencies.

## Flow
- Page 1 “Waar zitten de flitsen?” upload → zoom/pan → coarse pink ROI (brush/lasso, dilate a few px) → intensity slider (default felste) → “Detecteer in selectie” → yellow preview ONLY inside ROI → “Invullen/Volgende”.
- Page 2 “Nakijken”: filled result, before/after toggle, “Extra puntje weg” (click → detect in small window + fill; or mini-ROI brush → detector clipped), “Herstellen” (copy pixels back from original + 1px seam), undo, export same format (PNG→PNG, JPEG→JPEG q1.0).
- Original bitmap kept in memory. Detection NEVER outside ROI. Fill only accepted pixels (spec + small halo), local median of unmasked neighbours in a disk larger than the spec. No stripe healing, no region-wide inpaint, no diffusion.

## Detection (ROI only), dual path OR, clipped:
- Path A dark cloth: luma vs robust local background (median-based, outlier-resistant); white-on-dark shortcut when many white dots cluster.
- Path B mid/light: top-hat (luma − opened background) + annulus/ring test (ring clearly darker than blob → island; bright ring → reject as highlight/sheen).
- Must be: small (diameter capped vs long edge), compact/round-ish, very bright + low saturation (white/grey, not gold/skin), a peak vs opened background, isolated (dark ring).
- Must NOT: long thin fibres (reject elongated), dense sparkle fields unless discrete fat blobs, broad bright plateaus (bright ring → reject).
- Intensity 0..1 (default ~0.75 “felste”): drives peak margin, min whiteness, ring contrast, max spec size.
- Halo: dilate accepted specs 1-3 px, never outside (dilated) ROI.

## UI copy (Dutch)
Page 1: “Markeer grof de gebieden met flits. Alleen dáár zoekt de tool de felste witte stippen. Strepen en verfhighlights buiten (en zoveel mogelijk binnen) de markering blijven staan.”
Page 2: “Controleer het resultaat. Klik of sleep extra flitsstippen weg. Gebruik Herstellen als er per ongeluk een echte highlight is verdwenen.”
