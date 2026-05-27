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
```python
resp = client.chat.batch(prompt=["A", "B"])   # non‑streaming, accessible without iteration
print(resp.results)   # warning: results is empty
```

✅ **Correct:** Specify `keep=["results"]` (or `keep=["*"]`) to preserve `.results`.
```python
resp = client.chat.batch(prompt=["A", "B"], keep=["results"])
print(resp.results)   # now available
```

3. **Mixing batch-level and per-request `stop_on_error`**
- `stop_on_error` only works as batch-level parameter, not inside per-request dict. If not configured, errors are isolated.

4. **Using `print(resp)` or `print(chunk.still, end="")` inside `with resp.repr as view:`**
```python
with resp.repr as view:
    for chunk in resp:
        print(chunk.still, end="")  # ❌ conflicts with Rich Live ANSI control
        view.refresh()
```

✅ **Correct:** feed data to non-terminal destinations (frontend UI, list, etc.)
```python
frontend = []
with resp.repr as view:
    for chunk in resp:
        frontend.append(chunk.still)  # feed to UI/log; no print()
        view.refresh()
```

5. **Skipping iteration in mixed batch (stream + non-stream)**
```python
resp = client.chat.batch(requests=[
    {"prompt": "A", "stream": True},
    {"prompt": "B"},
])
print(resp.still)  # ❌ still is empty — no iteration was done
```

✅ **Correct:** mixed batch **must be iterated** to trigger request processing.
```python
for _ in resp:
    pass
print(resp.still)  # ✅ now available
```

6. **Using `resp.still` inside streaming loop and wondering why it grows**
```python
for chunk in resp:
    print(resp.still)  # prints FULL accumulated content, not delta
```

✅ **Correct:** use `chunk.still` for per-chunk delta; use `resp.still` after iteration.
```python
for chunk in resp:
    print(chunk.still)  # per-chunk delta
print(resp.still)  # full accumulated result
```

7. **Calling `resp.wait()` on mixed/streaming batch**
```python
resp = client.chat.batch(requests=[...], stream=True)
resp.wait()  # ❌ no-op — mixed/streaming batch has no background thread
```

✅ **Correct:** iteration drives execution.
```python
for _ in resp:
    pass
```

8. **Assuming batch streaming chunks contain a `message` key**
```python
for chunk in resp:
    print(chunk["choices"][0]["message"]["content"])  # ❌ KeyError: 'message'
```

✅ **Correct:** streaming chunks use `delta` format.
```python
for chunk in resp:
    print(chunk["choices"][0]["delta"].get("content", ""))
# Or use: chunk.still
```
