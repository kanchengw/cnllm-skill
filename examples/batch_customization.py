"""Batch with custom IDs and callbacks"""
import os
from cnllm import CNLLM

def on_complete(req_id, status):
    print(f"Request {req_id} finished with {status}")  # Define any custom logic here

client = CNLLM(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_KEY", "your-key"))

resp = client.chat.batch(
    prompt=["Task A", "Task B", "Task C"],
    custom_ids=["job_001", "job_002", "job_003"],
    callbacks=[on_complete],
)

# Iterate to execute batch and see real-time progress
for _ in resp:
    print(resp.status)

print("Final results:", resp.results)
print("Errors:", resp.errors)