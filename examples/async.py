"""Async client usage."""
import asyncio
import os
from cnllm import asyncCNLLM

async def main():
    client = asyncCNLLM(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_KEY", "your-key"))
    resp = await client.chat.create(prompt="Tell me a joke", stream=True)
    async for chunk in resp:
        print(resp.still, end="", flush=True)
    print()
    await client.aclose()

asyncio.run(main())