> **[🇬🇧 English](README.md) | [🇫🇷 Français](README.fr.md)**

# LLM Router : Smart router for local LLM models

![Docker](https://img.shields.io/badge/docker-compose-2496ED)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![License](https://img.shields.io/badge/license-MIT-green)


**LLM Router** is an API server that automatically analyzes your prompts and selects the best model among your local models.
No more manually choosing between code, reasoning, chat, or vision — the router decides for you.

```
┌─────────────┐    ┌──────────────┐    ┌────────────┐    ┌──────────────┐
│  User       │───▶│  OpenWebUI   │───▶│ LLM Router │───▶│   Ollama     │
│             │    │   (:3000)    │    │   (:5000)   │    │  (:11434)    │
└─────────────┘    └──────────────┘    └──────┬─────┘    └──────┬───────┘
                                             │                   │
                                    config / cache / logs ───────┘
```

---

## Features

✅ **Intelligent semantic routing** — Cosine similarity embeddings + keyword boost + speed bonus

✅ **Smart cache** — In-memory responses (Redis-ready for NAS)

✅ **Session memory** — Conversation history

✅ **Structured logging** — Trace of every request and routing decision

✅ **OpenAI API compatible** — OpenWebUI, Continue, and any OpenAI client

✅ **GPU support** — NVIDIA container toolkit acceleration

✅ **Docker Compose** — One-command deployment

---

## Service architecture

|    Service	|  Port	 |                Role                  |          URL            |
|-------------|--------|-------------------------------------|------------------------ |
| llm-router	| 5000	 | Intelligent routing API (FastAPI)   | http://localhost:5000   |
| ollama	    | 11434	 | Model server (GPU enabled)          | http://localhost:11434  |
| open-webui	| 3000	 | Web UI + RAG                        | http://localhost:3000   |

---

## File architecture

| File | Role |
|------|------|
| `config.py` | **Single source of truth** — models, URLs, keyword boosts, weights |
| `models.py` | Embeddings + precomputed reference vectors |
| `router.py` | Main logic — routing, streaming, endpoints |
| `main.py` | FastAPI entry point (`from router import app`) |
| `cache.py` | In-memory LRU cache (→ Redis on NAS) |
| `memory.py` | Session history (→ Redis on NAS) |
| `logs.py` | JSON logging of each request and routing |
| `docker-compose.yml` | Service orchestration (router, ollama, openwebui) |

---

## Installation

### 1. Prerequisites

- [Docker](https://docs.docker.com/engine/install/) + Docker Compose
- NVIDIA GPU: install [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

**Verify GPU access**

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Without NVIDIA GPU: remove the `deploy` block in `docker-compose.yml` (CPU operation possible).

### 2. Launch services

```bash
# Clone the project
git clone https://github.com/RemyDaubenfeld/llm-router.git
cd llm-router

# Stop system Ollama if present
sudo systemctl stop ollama
sudo systemctl disable ollama

# Launch Docker Compose
docker compose up -d --build
```

### 3. Download models

All models are stored in Ollama. To add one:

```bash
docker compose exec ollama ollama pull <model_name>
```

To find models: [Ollama](https://ollama.com/search)

> First launch can take 10-30 minutes depending on your connection and GPU.

**Recommended model to start**

If you're new, install `nomic-embed-text` first (used for routing):

```bash
docker compose exec ollama ollama pull nomic-embed-text
```

### Useful commands

```bash
docker compose exec ollama ollama list        # List models
docker compose exec ollama ollama ps          # Active models
docker compose logs -f llm-router             # Router logs in real time
docker compose restart llm-router             # Restart after config.py modification
docker compose pull                           # Update Docker images
```

---

## Usage

OpenWebUI can be configured in two different ways — **do not enable both at the same time**.

---

### Solution 1: Use the router (recommended)

The router automatically analyzes your prompt and chooses the most suitable model.

**Connections → OpenAI compatible API**
-> Admin settings → Connections → OpenAI compatible API:
- URL → `http://llm-router:5000/v1`
- API Key → `ia-local`

> The model selected in OpenWebUI is a **pass-through** — it doesn't matter which one you choose, the router decides the actual model based on the prompt content. Simply select any available model to enable the conversation.

---

### Solution 2: Use Ollama directly

No automatic routing — you choose the model yourself for each conversation.

**Connections → Ollama API**
-> Admin settings → Connections → Ollama API:
- URL → `http://ollama:11434`

> These URLs use Docker service names — do not use `localhost` which won't work from inside containers.

---

### Embedding model for RAG

If you use a knowledge base, install the embedding model first:

```bash
docker compose exec ollama ollama pull nomic-embed-text
```

---

### Direct API call

```bash
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Write a fibonacci function in Python"}],"stream":false}'
```

---

## Routing customization

Edit **config.py** to:
- Modify keyword boosts (keywords)
- Adjust weights (weight)
- Add / remove models

---

## Routing

For each prompt:
1. **Semantic embedding** (cosine similarity) via `nomic-embed-text` in Ollama
2. **Keyword boost** (+0.3) defined per model in `config.py`
3. **Speed bonus** (+0.05) for short prompts on fast models

To see which model is chosen in real time:

```bash
docker compose logs -f llm-router
```

---

## Router endpoints

- `GET  /health` — server status + cache size
- `GET  /v1/models` — list of models (OpenAI compatibility)
- `POST /v1/chat/completions` — main endpoint (stream or sync)

---

## Knowledge base (RAG)

OpenWebUI includes a native RAG system that works directly with `nomic-embed-text`.
Files are split into chunks, transformed into embeddings, and retrieved automatically based on the prompt.

**Embeddings configuration** (one time only)
-> Admin settings → Documents:
- Embedding model → `nomic-embed-text`
- URL → `http://ollama:11434`

**Create a knowledge base**
-> Workspace → Knowledge → + New knowledge base

Upload files or sync a folder — OpenWebUI automatically generates embeddings. For evolving projects, use **Upload a folder** so changes are taken into account.

**Use the knowledge base in a conversation**
In the chat, type `#` followed by your base name. OpenWebUI retrieves relevant passages and injects them into the context before sending to the router.

**Complete flow**
```
Question about a project
        ↓
OpenWebUI searches for relevant passages (nomic-embed-text)
        ↓
Injects these passages into the prompt
        ↓
Router → chooses the right model among those in `config.py`
        ↓
Contextualized answer
```

> Everything stays 100% local. The router doesn't need any modification.

---

## FAQ / Troubleshooting

**The model doesn't respond or the router returns error 500**
- Verify the model is downloaded: `docker compose exec ollama ollama list`
- Check logs: `docker compose logs llm-router`

**How to know which model was selected?**
```bash
docker compose logs -f llm-router | grep "Selected model"
```

**How to modify routing (keywords, weights)?**
Edit `config.py`, then restart the router:
```bash
docker compose restart llm-router
```

**How to add a new model?**
1. Add it to `config.py` (name, type, keywords, weights)
2. Download it: `docker compose exec ollama ollama pull <model_name>`
3. Restart the router: `docker compose restart llm-router`

**GPU is not used**
- Verify `nvidia-container-toolkit` is installed
- Run: `sudo nvidia-ctk runtime configure --runtime=docker`
- Restart Docker: `sudo systemctl restart docker`
- Verify: `docker run --rm --gpus all nvidia/cuda:12.0-base-ubuntu22.04 nvidia-smi`

**Recover disk space after deleting models**
```bash
docker compose exec ollama rm -rf /root/.ollama/models/
docker compose down -v  # Also deletes volumes
```

**How to reset completely?**
```bash
docker compose down -v --rmi all
docker system prune -a
```

---

## Best practices

- Use a dedicated model per task — the router handles it automatically
- Don't give too much context at once — work in small steps
- Regularly back up the Docker volume `open-webui` (history, accounts)

---

## Docker volumes

```bash
docker volume ls                           # List volumes
docker volume rm llm_router_open-webui     # Delete (erases history and accounts)
```
> Deleting a container does not delete its data — volumes are independent.

**Backup the OpenWebUI volume**
```bash
docker run --rm -v llm_router_open-webui:/data -v $(pwd):/backup alpine \
  tar czf /backup/open-webui-backup.tar.gz /data
```

---

## Automatic startup

All services restart automatically thanks to `restart: unless-stopped`.

To ensure Docker starts at boot:
```bash
sudo systemctl enable docker
```

---

## Environment variables

|   Variable   |                Default              |            Description            |
|--------------|------------------------------------|-----------------------------------|
| `OLLAMA_URL` | `http://ollama:11434/api/generate` | Ollama URL (auto via Docker) |

---

## Redis migration (NAS or other server)

The comments in `cache.py` and `memory.py` indicate exactly which lines to replace:

```bash
pip install redis
```

---

## License

MIT - free to use, modify, and distribute.

---

## Acknowledgements

- **Ollama** for local model execution
- **OpenWebUI** for the interface and RAG
- **FastAPI** for performance and simplicity