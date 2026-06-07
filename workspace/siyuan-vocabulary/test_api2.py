"""Test Qwen API with requests library (no httpx/SSL issues)."""
import os, json, requests

API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

resp = requests.post(url, json={
    "model": "qwen-plus",
    "messages": [
        {"role": "system", "content": "You are a vocabulary expert. Output only JSON."},
        {"role": "user", "content": "Group: abandon|抛弃 desert|遗弃 forsake|放弃 keep|保持 retain|保留 maintain|维持\nOutput: {\"groups\": [{\"name\": \"test\", \"words\": [\"...\"], \"reason\": \"...\"}]}"},
    ],
    "max_tokens": 300,
    "temperature": 0.3,
}, headers={
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}, timeout=60)

print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Model: {data.get('model')}")
    print(f"Usage: {data.get('usage')}")
    print(f"Response: {data['choices'][0]['message']['content']}")
else:
    print(f"Error: {resp.text[:500]}")
