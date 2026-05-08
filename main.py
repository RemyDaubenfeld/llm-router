# Single entry point — all logic is in router.py
# Launch: uvicorn main:app --host 0.0.0.0 --port 5000 --reload

from router import app  # noqa: F401