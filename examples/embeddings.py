"""Example: Embedding requests from files with custom_ids."""

import os
from cnllm import CNLLM

# ------------------------------------------------------------
# Helper: read text from a file
# ------------------------------------------------------------
def read_text_from_file(file_path: str) -> str:
    """Read text content from a file (UTF-8)."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

# ------------------------------------------------------------
# Initialize client with an embedding model
# ------------------------------------------------------------
# Supported embedding models: embedding-2, embedding-3, embedding-3-pro (GLM),
# text-embedding-v4/v3/v2/v1 (Qwen), embedding-v1/bge-large-zh/bge-large-en (Baidu)
client = CNLLM(
    model="embedding-3-pro",          # GLM embedding model
    api_key=os.getenv("GLM_API_KEY"), # or set directly
)

# ------------------------------------------------------------
# 1. Single embedding from a file
# ------------------------------------------------------------
print("=== Single embedding from file ===")
file_path = "sample.txt"   # assume this file exists
if os.path.exists(file_path):
    content = read_text_from_file(file_path)
    print(f"File content: {content[:80]}...")
    resp = client.embeddings.create(input=content)
    # Access vectors (embedding values)
    print(f"Vector length: {len(resp.vectors)}")
    print(f"First 5 vector values: {resp.vectors[:5]}")
    print(f"Token usage: {resp.usage}")
    # Note: single embedding response has no `.status` field; only batch responses have it.
else:
    print(f"File '{file_path}' not found; skipping.")

# ------------------------------------------------------------
# 2. Batch embedding from multiple files
# ------------------------------------------------------------
print("\n=== Batch embedding from multiple files ===")
file_list = ["doc1.txt", "doc2.txt", "doc3.txt"]
texts = []
valid_ids = []
for fname in file_list:
    if os.path.exists(fname):
        texts.append(read_text_from_file(fname))
        valid_ids.append(fname)
    else:
        print(f"Warning: {fname} not found; skipped.")

if texts:
    resp_batch = client.embeddings.batch(
        input=texts,
        custom_ids=valid_ids,   # use filenames as custom IDs
    )
    # Access .status (batch execution statistics)
    print(f"Batch status: {resp_batch.status}")   # e.g., {'success_count':3, 'fail_count':0, ...}
    # Access vectors by custom ID
    for req_id in valid_ids:
        vec = resp_batch.vectors[req_id]
        print(f"File '{req_id}': vector length = {len(vec)}")
    print(f"Batch usage: {resp_batch.usage}")
    if resp_batch.errors:
        print(f"Errors: {resp_batch.errors}")
else:
    print("No files found; batch embedding skipped.")

# ------------------------------------------------------------
# 3. (Optional) Using a directory of text files
# ------------------------------------------------------------
print("\n=== (Optional) Process all .txt files in a directory ===")
import glob
dir_path = "./docs"   # change to your directory
if os.path.isdir(dir_path):
    files = glob.glob(os.path.join(dir_path, "*.txt"))
    if files:
        all_texts = []
        all_ids = []
        for f in files:
            all_texts.append(read_text_from_file(f))
            all_ids.append(os.path.basename(f))
        resp_dir = client.embeddings.batch(input=all_texts, custom_ids=all_ids)
        print(f"Processed {len(all_ids)} files")
        print(f"Batch status: {resp_dir.status}")
        print(f"Total usage: {resp_dir.usage}")
        # Show sample vectors for first file
        if all_ids:
            first_id = all_ids[0]
            print(f"First 5 vector values for '{first_id}': {resp_dir.vectors[first_id][:5]}")
    else:
        print(f"No .txt files in '{dir_path}'.")
else:
    print(f"Directory '{dir_path}' not found; skipped.")