import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

# =========================
# SOURCE DE VÉRITÉ UNIQUE
# Config optimisée pour :
#   - 16GB RAM
#   - RTX 3050 Ti Mobile (4GB VRAM)
#   - Usage solo (OpenWebUI)
# =========================
MODELS = {
    "deepseek-coder:6.7b-instruct-q8_0": {
        "type": "code",
        "speed": "fast",
        "weight": 0.95,
        "keywords": ["code", "bug", "api", "sql", "php", "python", "fonction", "erreur", "script", "class", "debug", "programme"],
    },
    "llama3.1:8b-instruct-q4_K_M": {
        "type": "reasoning",
        "speed": "medium",
        "weight": 0.9,
        "keywords": ["pourquoi", "analyse", "explique", "compare", "différence", "comment", "raisonne", "démontre", "argue"],
    },
    "mistral:latest": {
        "type": "chat",
        "speed": "fast",
        "weight": 0.75,
        "keywords": ["bonjour", "salut", "merci", "aide", "question", "résume", "traduis", "reformule", "rédige"],
    },
    "gemma3:4b": {
        "type": "general",
        "speed": "fast",
        "weight": 0.7,
        "keywords": [],  # fallback général
    },
    "minicpm-v:8b-2.6-q2_K": {
        "type": "vision",
        "speed": "medium",
        "weight": 0.8,
        "keywords": ["image", "photo", "picture", "screenshot", "décris cette", "que vois-tu", "qu'est-ce que", "capture d'écran", "regarde cette", "analyse cette image"],
        "requires_image": True,  # flag utile si ton routeur supporte ça
    },
}