import requests, os

def embed(text: str):
    r = requests.post("https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        json={"model": "text-embedding-3-small", "input": text})
    return r.json()["data"][0]["embedding"] 