import time
import numpy as np
import requests
from config import MODELS, OLLAMA_URL

EMBED_MODEL = "nomic-embed-text"
EMBED_URL = OLLAMA_URL.replace("/api/generate", "/api/embeddings")


def embed(text: str) -> np.ndarray:
    """Generate an embedding vector via nomic-embed-text in Ollama."""
    r = requests.post(
        EMBED_URL,
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=300,
    )
    r.raise_for_status()
    return np.array(r.json()["embedding"], dtype=np.float32)


def build_model_vectors(retries: int = 10, delay: int = 3) -> dict:
    """
    Precomputes embedding vectors for each model type.
    Wait for Ollama to be ready before starting (useful at Docker boot).
    """
    for attempt in range(retries):
        try:
            return {
                model: embed(cfg["type"])
                for model, cfg in MODELS.items()
            }
        except Exception as e:
            if attempt < retries - 1:
                print(f"[models] Ollama not ready, retry {attempt + 1}/{retries} in {delay}s... ({e})")
                time.sleep(delay)
            else:
                raise RuntimeError(f"Cannot reach Ollama after {retries} attempts: {e}")