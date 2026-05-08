import logging
import time
from functools import wraps

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("llm-router")


def log_routing(prompt: str, model: str, scores: dict):
    short = prompt[:60].replace("\n", " ")
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    top_str = " | ".join(f"{m}: {s:.3f}" for m, s in top)
    logger.info(f"ROUTE  → [{model}]  prompt='{short}'  scores=({top_str})")


def log_cache_hit(prompt: str, model: str):
    short = prompt[:60].replace("\n", " ")
    logger.info(f"CACHE  ✓ [{model}]  prompt='{short}'")


def log_request(session_id: str, model: str, stream: bool):
    mode = "stream" if stream else "sync"
    logger.info(f"REQ    [{mode}] session={session_id[:8]}  model={model}")


def log_response(session_id: str, model: str, duration: float, tokens_approx: int):
    logger.info(f"RESP   session={session_id[:8]}  model={model}  {duration:.2f}s  ~{tokens_approx} tokens")


def timed(fn):
    """Utility decorator to measure execution time."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.time()
        result = fn(*args, **kwargs)
        logger.debug(f"{fn.__name__} executed in {time.time() - t0:.3f}s")
        return result
    return wrapper