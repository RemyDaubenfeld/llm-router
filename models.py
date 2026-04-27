import time
import numpy as np
import requests
from config import MODELS, OLLAMA_URL

EMBED_MODEL = "nomic-embed-text"
EMBED_URL = OLLAMA_URL.replace("/api/generate", "/api/embeddings")


def embed(text: str) -> np.ndarray:
    """Génère un vecteur d'embedding via nomic-embed-text dans Ollama."""
    r = requests.post(
        EMBED_URL,
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=30,
    )
    r.raise_for_status()
    return np.array(r.json()["embedding"], dtype=np.float32)


def build_model_vectors(retries: int = 10, delay: int = 3) -> dict:
    """
    Précalcule les vecteurs d'embedding pour chaque type de modèle.
    Attend qu'Ollama soit prêt avant de démarrer (utile au boot Docker).
    """
    for attempt in range(retries):
        try:
            return {
                model: embed(cfg["type"])
                for model, cfg in MODELS.items()
            }
        except Exception as e:
            if attempt < retries - 1:
                print(f"[models] Ollama pas encore prêt, retry {attempt + 1}/{retries} dans {delay}s... ({e})")
                time.sleep(delay)
            else:
                raise RuntimeError(f"Impossible de joindre Ollama après {retries} tentatives : {e}")