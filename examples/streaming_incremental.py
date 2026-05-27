"""
Single streaming — chunk.* incremental access + resp.repr live view.

Usage:
    python examples/streaming_incremental.py
"""
import os
from cnllm import CNLLM

client = CNLLM(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_KEY"))
resp = client.chat.create(
    messages=[{"role": "user", "content": "用一句话介绍北京"}],
    stream=True,
    thinking=True,
)

# ── Live view + incremental access in one loop ──
with resp.repr as view:
    for chunk in resp:
        # chunk.still / chunk.think are per-chunk deltas
        print(f"  delta content: {chunk.still!r}")
        if chunk.think:
            print(f"  delta think:   {chunk.think!r}")
        view.refresh()

# ── After stream: resp.* returns fully accumulated results ──
print(f"\nFull still: {resp.still}")
print(f"Full think: {resp.think}")
print(f"Full tools: {resp.tools}")
print(f"repr: {repr(resp)}")
