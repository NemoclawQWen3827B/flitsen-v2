import json, time, urllib.request, sys, re
from collections import Counter

BASE = "https://inference.local/v1/chat/completions"
model = "unsloth/Qwen3.8-27B-NVFP4"
spec = open("/sandbox/.openclaw/workspace/flitsen-v2/spec-v2.md").read()
part = open("/sandbox/.openclaw/workspace/flitsen-v2/gen-raw.txt").read()
# strip the leading fence so the model sees raw code
part = part[part.find('```html')+7:] if '```html' in part[:40] else part
part = part.strip('\n')

prompt = (
"You previously started generating a single-file HTML app (Flits-verwijderaar V2, Dutch UI, dark warm theme) from the spec below. "
"The stream was interrupted mid-file. Below is the EXACT content generated so far (HTML + CSS complete; <script> started; JS cut off mid-expression in function bindNav).\n\n"
"TASK: CONTINUE the file from EXACTLY the cut point. Do NOT repeat or regenerate any earlier content - your output must start exactly where the file was cut. "
"Finish the ENTIRE remaining application so the file is complete and runnable when the parts are concatenated, in this order: finish bindNav (wheel zoom at cursor, drag pan, pinch, clamp) and apply it to both pages; the coarse pink multi-region ROI brush + freehand lasso on page 1 (pointer painting on overlay, image-space, dilated a few px for detection); the single intensity segment control ('Alleen de felste' / 'Ook zwakkere witte stippen'); 'Detecteer in selectie' button -> run detection in the Web Worker with progress; the WORKER code (inline via Blob URL) implementing the dual-path detector and ALL component filters exactly as specified (strided sliding-median local background + MAD, top-hat path, whiteness, size/compactness/anti-scratch, ring isolation test, peak test, halo dilation clipped to dilated ROI, intensity parameter mapping, ROI masking so NOTHING outside the dilated ROI is ever detected, downscale note for >20MP); yellow preview overlay drawn ONLY inside the dilated ROI; 'Invullen' -> local median fill of accepted pixels+halo from nearby UNMASKED pixels in a slightly larger disk (no stripe healing, no region inpaint); page 2 'Nakijken' with before/after toggle (hold or toggle) and badges; 'Extra puntje weg' tool (click or tiny brush -> detector in a small clipped window around pointer, fill only if detected, otherwise do nothing); 'Herstellen' tool (paint over wrongly-removed pixels -> copy from original bitmap with 1px feathered seam); full undo stack covering fills, page-2 edits and restores; export in the ORIGINAL format (PNG->PNG, JPEG->JPEG quality 1.0) with download link + format label; status/count messages in Dutch; keep the original bitmap in memory. "
"UI copy: Dutch, warm and plain (Maartje-shape). All existing variable/function names in the partial file (view, paintState, roi, work, origU8, ctx1, ctx2, buildOverlay, drawBase, bindNav, cmpOn, render2, $, etc.) must be reused consistently; do not redeclare what already exists. The file must end with </script></body></html>. "
"STYLE: compact, professional code; write each rule/line once; no repeated or numbered-variant lines.\n\n"
"Return ONLY the continuation (from the cut point to </html>) in a single fenced code block (fenced html). No explanation inside.\n\n"
"=== SPEC (reference) ===\n" + spec + "\n\n=== FILE SO FAR (ends at cut point) ===\n" + part
)

body = json.dumps({
  "model": model,
  "messages": [{"role": "user", "content": prompt}],
  "max_tokens": 32768,
  "temperature": 0.4,
  "top_p": 0.9,
  "repetition_penalty": 1.1,
  "presence_penalty": 0.5,
  "stream": True,
  "chat_template_kwargs": {"enable_thinking": False}
}).encode()

def loop_detected(buf):
    tail = buf[-8000:]
    lines = tail.split('\n')[-40:]
    if len(lines) >= 40:
        norm = [re.sub(r'\d+', '#', l.strip()) for l in lines]
        c = Counter(norm)
        if c and c.most_common(1)[0][1] > 25:
            return 'repeated-lines:' + c.most_common(1)[0][0][:60]
    return None

t0 = time.time()
req = urllib.request.Request(BASE, data=body, headers={"Content-Type": "application/json"})
r = urllib.request.urlopen(req, timeout=1800)
out = []
buf = ""
last = 0
finish = None
while True:
    line = r.readline()
    if not line:
        break
    line = line.decode().strip()
    if not line.startswith("data:"):
        continue
    data = line[5:].strip()
    if data == "[DONE]":
        break
    try:
        d = json.loads(data)
    except Exception:
        continue
    ch = d.get("choices", [{}])[0]
    delta = ch.get("delta") or {}
    c = delta.get("content") or ""
    if c:
        out.append(c)
        buf = "".join(out)
        hit = loop_detected(buf)
        if hit:
            print(f"LOOP GUARD TRIPPED ({hit}) at {time.time()-t0:.0f}s, {len(buf)} chars - aborting early", flush=True)
            open("/sandbox/.openclaw/workspace/flitsen-v2/gen3-raw.txt", "w").write(buf)
            sys.exit(3)
    if ch.get("finish_reason"):
        finish = ch["finish_reason"]
    now = time.time()
    if now - last > 30:
        last = now
        print(f"... {len(buf)} chars, {now-t0:.0f}s", flush=True)

full = "".join(out)
open("/sandbox/.openclaw/workspace/flitsen-v2/gen3-raw.txt", "w").write(full)
print(f"GEN3 DONE chars={len(full)} finish={finish} elapsed={time.time()-t0:.0f}s", flush=True)
