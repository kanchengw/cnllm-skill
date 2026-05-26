---
name: cnllm-skill
description: |
  Use this skill when you need to call Chinese LLM APIs (DeepSeek, GLM, Qwen, etc.) with advanced features: per-request batch configuration,  automated streaming accumulation, streaming structural overview (streaming process inspection), vendor-native parameter validation with feedback, memory control, configurable failure policy, batch task progress tracking. Replaces OpenAI SDK/LiteLLM for multi-model workflows.
---

# CNLLM: Chinese LLM Unified Adapter

## When to Use This Skill (Exact Triggers)

- **Multi‑model workflows** – need to call different Chinese LLMs (e.g., DeepSeek vs GLM) in the same script.
- **Batch with per‑request config** – each request requires different `model`, `thinking`, `tools`, or `stream`.
- **Automated streaming accumulation** – need real‑time access to `reasoning_content`, `content`, and `tool_calls` via `.think`/`.still`/`.tools`.
- **Streaming structural overview** – need to monitor streaming process in a non-streaming-like structure.
- **Silent parameter failures** – need explicit feedback on unsupported parameters and configure handling behavior.
- **Memory‑constrained environments** – need to control memory usage.
- **Configurable failure policy** – need to configure how to handle errors within batch tasks.
- **Batch task progress tracking** – need to monitor the progress of batch tasks.

## Installation & Version

```bash
pip install cnllm
```

For latest features, ensure version >=0.9.3.

## Basic Principles

### 1. Initialize the client 
Note: Initialize the client with parameters you plan to use repeatedly, before invoking any API methods. Parameters at call time will override the parameters set in the client initialization.

```python
client = CNLLM(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_KEY")) # use default base_url - vendor's OpenAI-compatible url
resp = client.chat.create(prompt="Hello, world!", model="deepseek-v4-pro")
```

### 2. Unified Parameters
Use **OpenAI standard parameters**, configure vendor-native ones if needed, which CNLLM will passed to the vendor's API as-is if supported (pass these without `extra_body` ). 

### 3. HTTP Control Parameters
| Parameter         | Type    | Default    | Description          |
| ----------------- | ------- | ---------- | -------------------- |
| `timeout`         | `int`   | `60`       | Request timeout (seconds) |
| `max_retries`     | `int`   | `3`        | Maximum retry count  |
| `retry_delay`     | `float` | `1.0`      | Retry delay (seconds) |
| `max_concurrent`  | `int`   | `3`(chat)/`12`(embeddings) | Maximum concurrent requests, batch only |
| `rps`             | `int`   | `2`(chat)/`10`(embeddings) | Maximum requests per second, batch only |

## Minimal Working Examples

### 1. Streaming Chat with repr()
```python
import os
from cnllm import CNLLM

client = CNLLM(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_KEY")) 
resp = client.chat.create(messages=[{"role": "user", "content": "Hello"}], stream=True, thinking=True)
for chunk in resp:
    print(resp.think)  # real-time accumulated reasoning process
    print(resp)  # {'id': '...', 'object': '...', 'created': '...', 'model': '...', 'choices': [{'delta': {'content': 'real-time accumulated model response', 'reasoning_content': 'real-time accumulated reasoning process'}, 'finish_reason': 'None'}]}
print(resp.still)  # fully accumulated model response
```
Note: The `repr()` of streaming response displays **real-time results of chunk merging and field accumulation**; does not change the streaming response object type, which is an **iterator** containing all standard streaming chunks.

### 2. Per‑Request Batch
Note: batch-level controls will not be passed to individual requests, including `max_concurrent` , `rps`, `batch_size`, `keep`, `stop_on_error`, `callbacks`, `custom_ids`.

```python
resp = client.chat.batch(
    requests=[
        {"prompt": "Weather in Beijing", "model": "deepseek-v4-pro", "tools": [weather_tool]},
        {"prompt": "1+1=?", "model": "glm-5.1", "thinking": True},
        {"prompt": "Translate 'hello'", "model": "qwen-3.6-plus", "stream": False},
    ],
    stream=True,  # global default, inherited by per-request if not specified
    stop_on_error=True,  # batch-level control
)
```

## 3. Embeddings Batch
```python
resp = client.embeddings.batch(
    input=["Hello","Goodbye"],
    model="embeddings-3-pro",
)
```

### 4. Parameter Validation (`drop_params`) and Failure Policy (`stop_on_error`)
```python
resp = client.chat.batch(
    prompt=["A","B"],
    drop_params="strict",
    stop_on_error=True,
)
```
Note: 
- set `strict` to reject any unsupported parameter (request classified in `.errors`), or use `warn` to warn and continue, or `ignore` to silently drop.
- set `stop_on_error=True` to interrupt batch task on first error, or use `stop_on_error=False` to continue.

### Common Mistakes (Avoid These)

1. **Treating batch streaming response as a simple container**
```python
resp = client.chat.batch(prompt=["A","B"], stream=True)
print(resp.results)        # stream batch needs to be iterated
```

✅ **Correct:** iterate to execute
```python
for _ in resp:
    print(resp.status)     # real-time batch progress statistics
```

2. **Accessing `.results` after BatchResponse completes without keep=["results"]**
Note: 
- **`keep` default** retains essential fields: for chat.batch() retains only `.still`, `.think`, `.tools` and metadata (`.status`/`.usage`); for embeddings.batch() retains `.vectors` and metadata (`.status`/`.usage`/`.batch_info`).
- During iteration, all fields are available, independent of `keep`.
- Safer to declare wanted fields in `keep`.

```python
resp = client.chat.batch(prompt=["A", "B"])   # non‑streaming, accessible without iteration
print(resp.results)   # warning: results is empty
```

✅ **Correct:** Specify keep=["results"] (or keep=["*"]) to preserve `.results`.

```python
resp = client.chat.batch(prompt=["A", "B"], keep=["results"])
print(resp.results)   # now available
```

3. **Mixing batch-level and per-request `stop_on_error`**
   - `stop_on_error` only works as batch-level parameter, not inside per-request dict, if not configured, errors are isolated.


## Response Availability

| Scenario         | format      | Response Availability           |
| ---------------------- | --------- | ------------------------------------------------------- |
| **Non-streaming**      | OpenAI standard response format | Immediately available after `create()` returns.                  |
| **Streaming**          | OpenAI standard response format | Iterations required, update chunk by chunk during iteration, complete after iteration. |
| **Batch (non-stream)** | CNLLM batch response format, OpenAI standard responses in `.results` | Immediately available after `batch()` completes. Iteration is optional, if performed, all fields update request by request in real time. |
| **Batch (streaming)**  | CNLLM batch response format, OpenAI standard responses in `.results` | Iterations required, fields update chunk by chunk during iteration, complete after iteration. |

## Batch Response Structure

**chat.batch():**
```
{
    "status": {"elapsed": "3.42s", "success_count": 2, "fail_count": 1, "total": 3},  # Statistics
    "usage": {"prompt_tokens": 5, "total_tokens": 5},     # Batch processing total usage info
    "errors": {"request_2": "error message"},             # Mapping of all failed requests' request_id to error messages
    "results": {"request_0": {...}, "request_1": {...}},  # Mapping of all successful requests' request_id to standard responses
    "think": {"request_0": "...", "request_1": "..."},
    "still": {"request_0": "...", "request_1": "..."},
    "tools": {"request_0": {...}, "request_1": {...}},
    "raw": {"request_0": {...}, "request_1": {...}}
}
```

**embeddings.batch():**
```
{   
    "status": {"elapsed": "3.35s", "success_count": 1, "fail_count": 1, "total": 2},
    "batch_info": {"batch_size": 2, "batch_count": 2, "dimension": 1024},
    "usage": {"prompt_tokens": 5, "total_tokens": 5},
    "results": {"request_0": {...}, "request_1": {...}}
    "errors": {"request_2": "error message"},
    "vectors": {"request_0": [...], "request_1": [...]}    # Mapping of all successful requests' request_id to embedding vectors
}
```

## Advanced Examples (See `examples/` directory)

fallback.py – multi‑model fallback with detailed error handling
async.py – async client usage with asyncCNLLM
langchain_integration.py – built-in integration with LangChain Runnable.
batch_customization.py – custom IDs and callbacks
## Supported Vendors (Model List see `docs/model_list.md`)
DeepSeek, GLM (Zhipu), KIMI (Moonshot), MiniMax, Doubao (ByteDance), Xiaomi mimo, Qwen (Alibaba), Ernie (Baidu), Hunyuan (Tencent). See full list in project README.