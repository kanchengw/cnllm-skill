"""
Batch streaming — chunk.* per-request routing + resp.repr.

Usage:
    python examples/batch_streaming.py
"""
import os
from cnllm import CNLLM

client = CNLLM(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_KEY"))
resp = client.chat.batch(
    prompt=["北京的天气", "上海的天气"],
    stream=True,
)

frontend = {"request_0": "", "request_1": ""}

with resp.repr as view:
    for chunk in resp:
        rid = chunk["request_id"]
        frontend[rid] += chunk.still  # auto-routed by request_id
        view.refresh()

print("\nPer-request results:")
for rid, text in frontend.items():
    print(f"  {rid}: {text[:80]}")

print(f"\nresp.still: {resp.still}")
print(f"resp.status: {resp.status}")
