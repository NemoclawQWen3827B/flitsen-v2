import json, time, urllib.request, sys, re
from collections import deque

BASE = "https://inference.local/v1/chat/completions"
model = "unsloth/Qwen3.8-27B-NVFP4"
spec = open("/sandbox/.openclaw/workspace/flitsen-v2/spec-v2.md").read()

prompt = (
"You are a senior frontend engineer. Build the product specified below.\n\n"
"Deliverable: ONE single self-contained file (call it index.html) - pure HTML+CSS+vanilla JS, no dependencies, no network calls, no AI. "
"Inline the Web Worker via Blob URL (no separate .js file). "
"Return ONLY the complete final code in a single fenced code block (fenced html), no placeholders, no TODOs, no explanation inside the block. "
"After the code block, add at most 5 bullet points of implementation notes (key parameters chosen, how the worker protocol works, known edge cases).\n\n"
"STYLE RULES (important): keep the code compact and professional. Write each CSS rule ONCE. Never generate repeated or near-identical lines. "
"No decorative repetition, no numbered class variants. Efficient, dense, clean code.\n\n"
"Hard requirements: everything in the spec below - two pages (ROI marking page, then inspect page), wheel-zoom/pan on both pages, "
"coarse pink multi-region ROI brush, detection ONLY inside the slightly-dilated ROI, dual-path white-peak detector "
"(strided sliding-median background path + top-hat path) with component filters (size, compactness/anti-scratch, ring isolation test), "
"single intensity slider (Dutch labels: 'Alleen de felste' default, 'Ook zwakkere witte stippen'), yellow preview inside ROI only, "
"local median fill of accepted blobs + halo, page 2 with before/after toggle, 'Extra puntje weg' mini-ROI click tool, "
"'Herstellen' restore-from-original tool with 1px seam feather, undo stack, export in original format (PNG->PNG, JPEG->JPEG q=1.0). "
"All UI copy in Dutch, warm and plain. Keep the original bitmap in memory. Handle up to ~20MP working copy (downscale larger, note it). "
"Detection must run in the Web Worker; show progress. Code must be complete and runnable when saved as index.html.\n\n"
"=== SPEC ===\n" + spec
)

body = json.dumps({
  "model": model,
  "messages": [{"role": "user", "content": prompt}],
  "max_tokens": 32768,
  "temperature": 0.4,
  "top_p": 0.9,
  "repetition_penalty": 1.15,
  "presence_penalty": 0.5,
  "stream": True,
  "chat_template_kwargs": {"enable_thinking": False}
}).encode()

def loop_detected(buf):
    tail = buf[-8000:]
    if len(re.findall(r'#stage\.brush\d+\{', tail)) > 8:
        return 'brushN-loop'
    lines = tail.split('\n')[-40:]
    if len(lines) >= 40:
        norm = [re.sub(r'\d+', '#', l.strip()) for l in lines]
        from collections import Counter
        c = Counter(norm)
        if c and c.most_common(1)[0][1] > 25:
            return 'repeated-lines:' + c.most_common(1)[0][0][:60]
    return None

t0 = time.time()
req = urllib.request.Request(BASE, data=body, headers={"Content-Type": "application/json"})
r = urllib.request.urlopen(req, timeout=1500)
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
            open("/sandbox/.openclaw/workspace/flitsen-v2/gen-raw.txt", "w").write(buf)
            open("/sandbox/.openclaw/workspace/flitsen-v2/build.log", "a").write("LOOP_ABORT\n")
            sys.exit(3)
    if ch.get("finish_reason"):
        finish = ch["finish_reason"]
    now = time.time()
    if now - last > 30:
        last = now
        print(f"... {len(buf)} chars, {now-t0:.0f}s", flush=True)

full = "".join(out)
open("/sandbox/.openclaw/workspace/flitsen-v2/gen-raw.txt", "w").write(full)
print(f"GEN DONE chars={len(full)} finish={finish} elapsed={time.time()-t0:.0f}s", flush=True)
