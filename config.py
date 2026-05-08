import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

# Example of model integration to the router
MODELS = {
    "qwen2.5-coder:7b": {
        "type": "code",
        "speed": "fast",
        "weight": 0.95,
        "keywords": ["agentic", "modification", "fichier"],
    }
}