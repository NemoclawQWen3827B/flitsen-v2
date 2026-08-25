#!/bin/bash
set -e
cd /sandbox/.openclaw/workspace/flitsen-v2
start=$(date +%s)
curl -sS --max-time 1500 https://node1.agentopsinference.com/v1/chat/completions \
  -H "Authorization: Bearer ${AGENTOPS_API_KEY}" \
  -H "Content-Type: application/json" \
  --data @node1-payload.json -o node1-response.json
end=$(date +%s)
echo "curl done in $((end-start))s"
python3 - <<'PY'
import json
b = json.load(open('/sandbox/.openclaw/workspace/flitsen-v2/node1-response.json'))
c = b['choices'][0]['message']['content']
open('/sandbox/.openclaw/workspace/flitsen-v2/node1-response.md','w').write(c)
print('chars:', len(c))
print('finish:', b['choices'][0].get('finish_reason'))
print('usage:', b.get('usage'))
PY
