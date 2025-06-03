import faiss
import json
import os
import requests

API_URL = "http://localhost:1234/v1/chat/completions"

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.IndexFlatL2(384)  # 384 = embedding size of MiniLM
memory_data = []
INDEX_FILE = "memory.index"
DATA_FILE = "memory_data.json"

def embed_text(text):
    return model.encode([text])[0]
def extract_facts(text):
    prompt = f"""
You are an assistant that extracts clear, concise facts from roleplay transcripts.

The transcript consists of lines labeled with character names or 'Narrator'. Each line contains either:
- Direct dialogue (e.g., Jack: "I never trusted that bridge.")
- Third-person narration (e.g., Narrator: The knight grips his sword.)

Your job is to extract ONLY **explicitly stated** facts from the text — no assumptions, no opinions unless directly said by a character.

Guidelines:
- Include facts stated in narration and dialogue.
- Do NOT infer anything not clearly stated.
- Do NOT reword or paraphrase — just extract.
- Output should be a clean bullet list.

Text:
\"\"\"{text}\"\"\"

Return only facts in this format:
- The knight doesn't trust the merchant.
- Jack is a miner.
- The forest is quiet.
"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "jesaisap",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that extracts factual info from roleplay."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }
    response = requests.post(API_URL, json=payload, headers=headers)
    return response.json()["choices"][0]["message"]["content"]

def add_memory(text):
    global memory_data
    vector = embed_text(text)
    index.add(vector.reshape(1, -1))
    memory_data.append(text)

def search_memory(query, top_k=10, max_results=5, distance_threshold=1.2, sort_by_distance=True):
    """
    Search memory for relevant entries based on a query.

    Args:
        query (str): The search query.
        top_k (int): Number of top matches to retrieve from FAISS (includes less relevant ones).
        max_results (int): Maximum number of results to return after filtering.
        distance_threshold (float): Maximum distance allowed to consider a memory relevant.
        sort_by_distance (bool): Whether to sort results by closest match first.

    Returns:
        List of tuples: [(text, distance), ...]
    """
    vector = embed_text(query)
    D, I = index.search(vector.reshape(1, -1), top_k)

    results = []
    for dist, idx in zip(D[0], I[0]):
        if idx == -1 or dist >= 1e38:  # Filter out FAISS garbage
            continue
        if dist <= distance_threshold and idx < len(memory_data):
            results.append((memory_data[idx], float(dist)))

    if sort_by_distance:
        results.sort(key=lambda x: x[1])  # Sort by smallest distance first

    return results[:max_results]  # Trim to max results

def save_memory():
    faiss.write_index(index, INDEX_FILE)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, indent=2)

def load_memory():
    global index, memory_data
    if os.path.exists(INDEX_FILE):
        index = faiss.read_index(INDEX_FILE)
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            memory_data = json.load(f)