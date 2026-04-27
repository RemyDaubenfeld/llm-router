> **[🇬🇧 English](README.md) | [🇫🇷 Français](README.fr.md)**

# LLM Router V4.1

![Docker](https://img.shields.io/badge/docker-compose-2496ED)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![License](https://img.shields.io/badge/license-MIT-green)


## Intelligent router for local LLMs

Automatically selects the best model based on your prompt (code, reasoning, chat, vision).  
Optimized for **16 GB RAM + RTX 3050 Ti Mobile (4 GB VRAM)**.

```
User → OpenWebUI (:3000) → LLM Router (:5000) → Ollama (:11434) → Models
                                        |
            OpenCode (terminal) ↗      config / models / cache / memory / logs
```

---

## Prerequisites

- [Docker](https://docs.docker.com/engine/install/) + Docker Compose
- NVIDIA GPU: install [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

# Verify that Docker can access the GPU
```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

If you don't have an NVIDIA GPU, remove the deploy block from **docker-compose.yml** — the project will run on CPU.

---

## Features

✅ Semantic routing (cosine similarity) + keyword boost + speed bonus

✅ In-memory intelligent cache (Redis ready)

✅ Session memory to track conversations

✅ Structured logging of every request and routing

✅ OpenAI API compatible → OpenWebUI, Continue, etc.

✅ GPU support via NVIDIA container toolkit

✅ Docker Compose “just run”

---

## Built-in models (configured in config.py)

|                Modèle               |  VRAM  |   Type    |           Cas d'usage              |
|-------------------------------------|--------|-----------|----------------------------------- |
| `deepseek-coder:6.7b-instruct-q8_0` | ~4GB   | code      | Bug, SQL, API, scripts             |
| `llama3.1:8b-instruct-q4_K_M`       | ~4GB   | reasoning | Analysis, explanation, comparison  |
| `mistral:latest`                    | ~4GB   | chat      | Short questions, conversation      |
| `gemma3:4b`                         | ~3GB   | general   | General fallback                   |
| `minicpm-v:8b-2.6-q2_K`             | ~4GB   | vision    | Image, photo, visual description   |
| `nomic-embed-text`                  | ~270MB | embedding | nternal semantic routing           |
 
 ---

 ## Service architecture

|    Service	|  Port	 |                Rôle                |          URL            |
|---------------|--------|------------------------------------|------------------------ |
| llm-router	| 5000	 | Intelligent routing API (FastAPI)  | http://localhost:5000   |
| ollama	    | 11434	 | Model server (GPU enabled)         | http://localhost:11434  |
| open-webui	| 3000	 | Web UI + RAG                       | http://localhost:3000   |

---

## File architecture

| Fichier     |                      Rôle                             |
|-------------|-------------------------------------------------------|
| `config.py` | **Single source of truth**: models, URL, keywords     |
| `models.py` | Embeddings via nomic-embed-text + precomputed vectors |
| `router.py` | Main logic: routing, streaming, endpoints             |
| `main.py`   | Entry point (from router import app)                  |
| `cache.py`  | In-memory cache (→ Redis on NAS)                      |
| `memory.py` | Session history (→ Redis on NAS)                      |
| `logs.py`   | Structured logging of every request/routing           |

---

## Quick installation

```bash
# 1. Clone the repository
git clone https://github.com/RemyDaubenfeld/llm-router.git
cd llm-router

# 2. If a system Ollama is running, stop it
sudo systemctl stop ollama
sudo systemctl disable ollama

# 3. Start all services
docker compose up -d --build

# 4. Pull recommended models (do this once after first start)
docker compose exec ollama ollama pull deepseek-coder:6.7b-instruct-q8_0
docker compose exec ollama ollama pull llama3.1:8b-instruct-q4_K_M
docker compose exec ollama ollama pull mistral:latest
docker compose exec ollama ollama pull gemma3:4b
docker compose exec ollama ollama pull minicpm-v:8b-2.6-q2_K
docker compose exec ollama ollama pull nomic-embed-text

# Other useful commands:
docker compose exec ollama ollama list        # list models
docker compose exec ollama ollama ps          # running models
docker compose exec ollama ollama rm <model>  # delete a model
```

---

## Usage

# 1. OpenWebUI (graphical interface)
**Connections → OpenAI compatible API**
-> Admin settings → Connections → OpenAI compatible API :
URL → http://llm-router:5000/v1
API Key → ia-local

**Connections → Ollama API** (for RAG embeddings)
-> Admin settings → Connections → Ollama API :
URL → http://ollama:11434

>These URLs use Docker service names — do not use localhost as it would not work from inside containers.

**Selecting a model in OpenWebUI**
The model selected in OpenWebUI is a **pass-through** — no matter which you choose, the router decides the actual model based on the prompt content.

# 2. OpenCode (terminal AI agent)
See the **OpenCode-guide-en.md** file included in the project.

# 3. Direct API call

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

## Routing logic

For each prompt:
1. **Semantic embedding** (cosine similarity) via nomic-embed-text in Ollama
2. **Keyword boost** (+0.3) defined per model in config.py
3. **Speed bonus** (+0.05) for short prompts on fast models

To see which model is chosen in real time:

```bash
docker compose logs -f llm-router
```

---

## Router endpoints

- `GET /health` — server status + cache size
- `GET /v1/models` — list of models (OpenAI compatibility)
- `POST /v1/chat/completions` — main endpoint (stream or sync)

---

## Knowledge base (RAG)

OpenWebUI includes a native RAG system that works directly with `nomic-embed-text`.
Files are split into chunks, transformed into embeddings, and retrieved automatically based on the prompt.

**Embeddings configuration** (one time only)
-> Admin settings → Documents :
- Embedding model → `nomic-embed-text`
- URL → `http://ollama:11434`

**Create a knowledge base**
-> Workspace → Knowledge → + New knowledge base

Upload your files or sync a folder — OpenWebUI generates embeddings automatically. For an evolving project, use **Upload a folder** so changes are taken into account.

**Use the knowledge base in a conversation**
In the chat, type `#` followed by the name of your knowledge base. OpenWebUI retrieves relevant passages and injects them into the context before sending to the router.

**Full flow**

Question about your project
        ↓
OpenWebUI searches for relevant passages (nomic-embed-text)
        ↓
Injects those passages into the prompt
        ↓
Router → chooses the right model (deepseek, llama, mistral...)
        ↓
Contextualized answer

>Everything remains 100% local. The router does not need any modification.

---

## Best practices

- Use a dedicated model per task — the router handles it automatically
- Don’t give too much context at once — work in small steps
- For code → let the router choose (deepseek will be selected)
- For analysis → let the router choose (llama will be selected)
- Regularly back up the Docker volume `open-webui` (history, accounts)

---

## Docker volumes

```bash
docker volume ls                           # list volumes
docker volume rm llm_router_open-webui     # delete (erases history and accounts)
```
>Deleting a container does not delete its data — volumes are independent.

**Backup the OpenWebUI volume**
```bash
docker run --rm -v llm_router_open-webui:/data -v $(pwd):/backup alpine \
  tar czf /backup/open-webui-backup.tar.gz /data
```

---

## Automatic startup

All services restart automatically thanks to `restart: unless-stopped`.

To ensure Docker starts at boot:
```bash
sudo systemctl enable docker
```
--- 

## Environment variables

|   Variable   |                Default             |            Description            |
|--------------|------------------------------------|-----------------------------------|
| `OLLAMA_URL` | `http://ollama:11434/api/generate` | Ollama URL (automatic via Docker) |

---

## GPU optimizations (for this setup)

In **docker-compose.yml**, the `ollama` service already includes:

```yaml
environment:
  - OLLAMA_GPU_OVERHEAD=2147483648
  - OLLAMA_FLASH_ATTENTION=1
  - OLLAMA_KV_CACHE_TYPE=q4_0
  - OLLAMA_NUM_PARALLEL=4
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

These settings enable partial GPU offloading and better memory management.

---

## Redis migration (NAS)
The comments in **cache.py** and **memory.py** indicate exactly which lines to replace:

```bash
pip install redis
```

---

## License

MIT — free to use, modify, and distribute.

---

## Acknowledgements
- **Ollama** for local model execution
- **OpenWebUI** for the interface and RAG
- **OpenCode** for the terminal agent
- **FastAPI** for performance and simplicity