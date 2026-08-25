#!/bin/bash
# Build Flitsen V2 index.html via local vLLM (node1 public API is down: no_db_connection)
set -e
cd /sandbox/.openclaw/workspace/flitsen-v2
echo "$(date -Is) START"
python3 - <30:
        last=now
        print(f'... {len("".join(out))} chars, {now-t0:.0f}s', flush=True)
full="".join(out)
open('gen-raw.txt','w').write(full)
print('GEN DONE chars:',len(full),'finish:',finish,f'elapsed {time.time()-t0:.0f}s', flush=True)
PY
python3 - <<'PY'
import re
t=open('gen-raw.txt').read()
m=re.findall(r'```(?:html)?\n(.*?)```', t, re.S)
if m:
    code=max(m,key=len)
    open('index.html','w').write(code)
    print('index.html written:', len(code), 'chars')
elif '<html' in t.lower() or '<!doctype' in t.lower():
    open('index.html','w').write(t)
    print('wrote raw as index.html (no fence found)')
else:
    print('NO FENCED BLOCK FOUND - check gen-raw.txt')
PY
echo "$(date -Is) FINISHED"
