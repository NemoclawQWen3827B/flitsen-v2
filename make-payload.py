import json
spec = open('/sandbox/.openclaw/workspace/flitsen-v2/spec-v2.md').read()
prompt = (
"You are building a product. Below is the COMPLETE, canonical build spec for 'Flits-verwijderaar V2' (a Dutch photo tool that removes flash reflections from painting photos).\n\n"
"Deliverable: ONE single self-contained file: /sandbox/.openclaw/workspace/flitsen-v2/index.html - pure HTML+CSS+vanilla JS, no dependencies, no network calls, no AI. Inline the Web Worker via Blob (no separate .js file). Return ONLY the complete final code in a single fenced code block (fenced html), no placeholders, no TODOs, no explanation inside the block. After the code block, add at most 5 bullet points of implementation notes (key parameters chosen, how the worker protocol works, known edge cases).\n\n"
"Hard requirements:\n"
"- Everything in the spec: two pages, zoom/pan, pink multi-region ROI brush (coarse), Web Worker detection clipped to slightly dilated ROI, dual-path detector with all component filters, single intensity slider (default 'Alleen de felste'), yellow preview only inside ROI, local-median fill with small halo clipped to dilated ROI, page 2 with before/after toggle, 'Extra puntje weg' (click/tap -> detect in small mini-ROI window around pointer, fill only if found), 'Herstellen' (brush restore from original + 1px seam blend), undo stack, format-preserving export (PNG->PNG, JPEG q=1.0), original bitmap kept in memory.\n"
"- All UI copy in Dutch, exactly the screen copy from the spec.\n"
"- Keep the file readable: small clean functions, constants at top with the spec default values, comments where the spec formulas apply.\n"
"- Must actually run: fix any bug you can reason about now (correct connected-components labeling, correct median filtering, correct JPEG/PNG encoding via canvas.toBlob with the right mime and quality).\n\n"
"SPEC (verbatim, complete):\n===SPEC-BEGIN===\n" + spec + "\n===SPEC-END===\n\n"
"Build it now. Quality bar: this ships to a non-technical user (Maartje) who marks pink regions roughly and must trust the tool never to touch unmarked areas. Correctness > cleverness."
)
payload = {"model": "gx10-coder", "messages": [{"role": "user", "content": prompt}], "max_tokens": 16000}
open('/sandbox/.openclaw/workspace/flitsen-v2/node1-payload.json', 'w').write(json.dumps(payload))
print('payload bytes:', len(json.dumps(payload)))
