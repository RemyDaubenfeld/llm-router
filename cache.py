# Cache en mémoire — remplacer par Redis lors du passage sur NAS :
#
#   import redis
#   r = redis.Redis(host="localhost", port=6379, db=0)
#   def get_cache(prompt, model): return r.get(make_key(prompt, model))
#   def set_cache(prompt, model, response): r.setex(make_key(prompt, model), 3600, response)

import hashlib

CACHE: dict[str, str] = {}


def make_key(prompt: str, model: str) -> str:
    return hashlib.md5((model + prompt).encode()).hexdigest()


def get_cache(prompt: str, model: str) -> str | None:
    return CACHE.get(make_key(prompt, model))


def set_cache(prompt: str, model: str, response: str) -> None:
    CACHE[make_key(prompt, model)] = response


def cache_size() -> int:
    return len(CACHE)