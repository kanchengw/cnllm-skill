"""
Mixed batch (stream + non-stream) — chunk.* for streaming, resp.* after iteration.

IMPORTANT: Mixed batch MUST be iterated to trigger request processing.
After iteration, all resp.* fields become available.

Usage:
    python examples/mixed_batch.py
"""
import os
from cnllm import CNLLM

client = CNLLM(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_KEY"))
resp = client.chat.batch(requests=[
    {"prompt": "北京的天气", "stream": True, "tools": [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather",
            "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}
        }
    }]},
    {"prompt": "1+1=?"},  # non-streaming
    {"prompt": "介绍北京", "stream": True},
])

frontend = {"request_0": "", "request_1": "", "request_2": ""}

# Only request_0 and request_2 (stream=True) yield chunks
for chunk in resp:
    frontend[chunk["request_id"]] += chunk.still  # empty string for markers, content for deltas

print("Per-request streaming results:")
for rid, text in frontend.items():
    if text:
        print(f"  {rid}: {text[:80]}")

# After iteration, all requests have accumulated results
print(f"\nStill: {resp.still}")
print(f"Tools: {resp.tools}")
print(f"Status: {resp.status}")
