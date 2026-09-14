# Flits-verwijderaar V2

Guided, region-first flash restorer for painting photos. One self-contained `index.html`. No AI, no network, no dependencies.

Open the file in a browser (Chrome, Edge, Firefox, Safari). JPEG stays JPEG (quality 1.0); PNG stays PNG.

## Flow

1. **Upload** a painting photo. The original bitmap stays in memory.
2. **Mark** roughly where flash lives (pink brush or lasso). Overshooting is fine.
3. Choose **Alleen de felste** vs **Ook zwakkere witte stippen**.
4. **Detecteer in selectie** — yellow dots appear only inside the (slightly dilated) pink region.
5. **Invullen** fills those specs with a local median of nearby unmasked pixels.
6. **Nakijken** — pick off leftovers, restore real highlights, undo, export.

Detection never runs outside the painted region. It is not iPhoto retouch: long scratches, canvas weave, hair highlights and painted halos are rejected.

On real painting photos: mark the dark varnish where flash lives, then **Detecteer**. Use the intensity slider if weaker specks remain; pick leftovers off on page 2. Do not paint over a halo or white hair if you can avoid it — those are highlights, not flash.

## Spec

See [spec-v2.md](spec-v2.md).
