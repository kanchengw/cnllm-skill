"""Multi-model fallback demonstration."""
import os
from cnllm import CNLLM, FallbackError

client = CNLLM(
    model="unavailable-model",
    api_key="dummy",
    fallback_models={
        "deepseek-chat": {"api_key": os.getenv("DEEPSEEK_KEY", "your-key"), "base_url": "https://api.deepseek.cn/api/v1"}, 
        "glm-4.7-flash": {"api_key": os.getenv("GLM_KEY", "your-key")},  # Key is required, base_url default is vendor's OpenAI-compatible url
    }
)
try:
    resp = client.chat.create(prompt="Hello, world!")
    print(resp.still)
except FallbackError as e:
    print(e)