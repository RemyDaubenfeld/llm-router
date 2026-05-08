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

app = FastAPI(title="LLM Router", version="4.2")

MODEL_VECTORS = build_model_vectors()

# URL for chat API (different from api/generate)
OLLAMA_CHAT_URL = OLLAMA_URL.replace("/api/generate", "/api/chat")


# =========================
# 🧠 SMART ROUTING
# =========================
def select_model(prompt: str) -> tuple[str, dict]:          
    """
    Selects the best model via:
    1. Cosine similarity (semantic embedding)
    2. Keyword boost specific to each model
    3. Speed bonus for short prompts
    Fallback to keywords only if Ollama is busy (avoids model swap).
    Returns (model_name, scores_dict) for logging.
    """
    p = prompt.lower()
    scores: dict[str, float] = {}

    # Attempt semantic embedding
    try:
        vec = embed(p)
        for model, cfg in MODELS.items():
            mv = MODEL_VECTORS[model]
            sim = np.dot(vec, mv) / (np.linalg.norm(vec) * np.linalg.norm(mv) + 1e-9)
            score = float(sim) * cfg["weight"]

            if any(kw in p for kw in cfg.get("keywords", [])):
                score += 0.3

            if len(p) < 30 and cfg["speed"] == "fast":
                score += 0.05

            scores[model] = score

    except Exception as e:
        # Fallback: keyword-only routing (no model swap)
        logger.warning(f"Embedding unavailable, fallback to keywords: {e}")
        for model, cfg in MODELS.items():
            score = cfg["weight"]
            if any(kw in p for kw in cfg.get("keywords", [])):
                score += 0.3
            if len(p) < 30 and cfg["speed"] == "fast":
                score += 0.05
            scores[model] = score

    best = max(scores, key=scores.get)
    return best, scores


# =========================
# 🚀 STREAM OLLAMA (api/chat)
# =========================
def stream_ollama(model: str, messages: list[dict]):
    """
    Generator of streamed chunks from Ollama via api/chat.
    Receives the complete message history (OpenAI format).
    """
    try:
        r = requests.post(
            OLLAMA_CHAT_URL,
            json={"model": model, "messages": messages, "stream": True},
            stream=True,
            timeout=120,
        )
        r.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error(f"Timeout Ollama for model {model}")
        yield "[ERROR: Ollama timeout]"
        return
    except requests.exceptions.ConnectionError:
        logger.error("Ollama unreachable")
        yield "[ERROR: Ollama unreachable]"
        return

    for line in r.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            # api/chat returns data["message"]["content"] (not data["response"])
            if "message" in data and "content" in data["message"]:
                chunk = data["message"]["content"]
                if chunk:
                    yield chunk


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
    """OpenAI compatibility endpoint for OpenWebUI."""
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
        raise HTTPException(status_code=400, detail="'messages' missing in body")

    # Prompt = last user message (for routing and cache)
    prompt = messages[-1]["content"]
    stream = body.get("stream", True)

    # Session
    session_id, _ = get_session(body.get("session_id"))
    add_message(session_id, "user", prompt)

    # Routing (based on the last message only)
    model, scores = select_model(prompt)
    log_routing(prompt, model, scores)

    # Cache (key = prompt + model)
    cached = get_cache(prompt, model)
    if cached:
        log_cache_hit(prompt, model)
        add_message(session_id, "assistant", cached)
        return _build_response(model, cached, cached=True)

    log_request(session_id, model, stream)
    t0 = time.time()

    # =========================
    # STREAM MODE
    # =========================
    if stream:
        def event_stream():
            full = ""
            # Pass full message history to Ollama
            for chunk in stream_ollama(model, messages):
                full += chunk
                yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk}}], 'model': model})}\n\n"

            set_cache(prompt, model, full)
            add_message(session_id, "assistant", full)
            log_response(session_id, model, time.time() - t0, len(full.split()))
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # =========================
    # SYNCHRONOUS MODE
    # =========================
    full = "".join(stream_ollama(model, messages))
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