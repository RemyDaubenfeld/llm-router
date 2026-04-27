import time
import json
import requests
import numpy as np
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse

from config import MODELS, OLLAMA_URL
from models import embed, build_model_vectors
from memory import get_session, add_message
from cache import get_cache, set_cache, cache_size
from logs import log_routing, log_cache_hit, log_request, log_response, logger

app = FastAPI(title="LLM Router", version="4.1")

# Vecteurs précalculés une seule fois au démarrage
MODEL_VECTORS = build_model_vectors()


# =========================
# 🧠 ROUTING INTELLIGENT
# =========================
def select_model(prompt: str) -> tuple[str, dict]:
    """
    Sélectionne le meilleur modèle via :
    1. Similarité cosinus (embedding sémantique)
    2. Boost par mots-clés spécifiques à chaque modèle
    3. Bonus vitesse pour les prompts courts
    Retourne (model_name, scores_dict) pour le logging.
    """
    vec = embed(prompt.lower())
    p = prompt.lower()
    scores: dict[str, float] = {}

    for model, cfg in MODELS.items():
        mv = MODEL_VECTORS[model]
        sim = np.dot(vec, mv) / (np.linalg.norm(vec) * np.linalg.norm(mv) + 1e-9)
        score = float(sim) * cfg["weight"]

        # Boost mots-clés — définis dans config.py par modèle
        if any(kw in p for kw in cfg.get("keywords", [])):
            score += 0.3

        # Bonus vitesse pour prompts courts
        if len(p) < 30 and cfg["speed"] == "fast":
            score += 0.05

        scores[model] = score

    best = max(scores, key=scores.get)
    return best, scores


# =========================
# 🚀 STREAM OLLAMA
# =========================
def stream_ollama(model: str, prompt: str):
    """Générateur de chunks streamés depuis Ollama."""
    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": True},
            stream=True,
            timeout=120,
        )
        r.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error(f"Timeout Ollama pour le modèle {model}")
        yield "[ERREUR : timeout Ollama]"
        return
    except requests.exceptions.ConnectionError:
        logger.error("Ollama inaccessible")
        yield "[ERREUR : Ollama inaccessible]"
        return

    for line in r.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            if "response" in data:
                yield data["response"]


# =========================
# 🔌 ENDPOINTS
# =========================
@app.get("/health")
def health():
    return {
        "status": "ok",
        "models": list(MODELS.keys()),
        "cache_entries": cache_size(),
    }


@app.get("/v1/models")
def list_models():
    """Endpoint de compatibilité OpenAI pour OpenWebUI."""
    return {
        "object": "list",
        "data": [
            {"id": m, "object": "model", "owned_by": "ollama"}
            for m in MODELS
        ],
    }


@app.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()

    messages = body.get("messages")
    if not messages:
        raise HTTPException(status_code=400, detail="'messages' manquant dans le body")

    prompt = messages[-1]["content"]
    stream = body.get("stream", True)

    # Session
    session_id, _ = get_session(body.get("session_id"))
    add_message(session_id, "user", prompt)

    # Routing
    model, scores = select_model(prompt)
    log_routing(prompt, model, scores)

    # Cache
    cached = get_cache(prompt, model)
    if cached:
        log_cache_hit(prompt, model)
        add_message(session_id, "assistant", cached)
        return _build_response(model, cached, cached=True)

    log_request(session_id, model, stream)
    t0 = time.time()

    # =========================
    # MODE STREAM
    # =========================
    if stream:
        def event_stream():
            full = ""
            for chunk in stream_ollama(model, prompt):
                full += chunk
                yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk}}], 'model': model})}\n\n"

            set_cache(prompt, model, full)
            add_message(session_id, "assistant", full)
            log_response(session_id, model, time.time() - t0, len(full.split()))
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # =========================
    # MODE SYNCHRONE
    # =========================
    full = "".join(stream_ollama(model, prompt))
    set_cache(prompt, model, full)
    add_message(session_id, "assistant", full)
    log_response(session_id, model, time.time() - t0, len(full.split()))

    return _build_response(model, full)


def _build_response(model: str, content: str, cached: bool = False) -> dict:
    return {
        "id": f"chatcmpl-{'cache' if cached else 'v4'}",
        "object": "chat.completion",
        "model": model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
    }