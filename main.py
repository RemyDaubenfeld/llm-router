# Point d'entrée unique — toute la logique est dans router.py
# Lancement : uvicorn main:app --host 0.0.0.0 --port 5000 --reload

from router import app  # noqa: F401