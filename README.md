# LLM Router V4.1

![Docker](https://img.shields.io/badge/docker-compose-2496ED)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![License](https://img.shields.io/badge/license-MIT-green)


## Routeur intelligent pour modèles LLM locaux

Sélection automatique du meilleur modèle selon le prompt (code, raisonnement, chat, vision).  
Optimisé pour **16 Go RAM + RTX 3050 Ti Mobile (4 Go VRAM)**.

```
Utilisateur → OpenWebUI (:3000) → LLM Router (:5000) → Ollama (:11434) → Modèles
                                                │
                  OpenCode (terminal) ↗     config / models / cache / memory / logs               
```

---

## Prérequis

- [Docker](https://docs.docker.com/engine/install/) + Docker Compose
- GPU Nvidia : installer [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

# Vérifier que le GPU est accessible par Docker
```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Sans GPU Nvidia, supprimer le bloc `deploy` dans le `docker-compose.yml` — le projet fonctionnera en CPU.

---

## Fonctionnalités

✅ Routing sémantique (cosine similarity) + boost par mots‑clés + bonus vitesse

✅ Cache intelligent en mémoire (prêt pour Redis)

✅ Mémoire de session pour suivre les conversations

✅ Logging structuré de chaque requête et routage

✅ Compatible OpenAI API → OpenWebUI, Continue, etc.

✅ Support GPU via NVIDIA container toolkit

✅ Docker Compose “prêt à l’emploi”

---

## Modèles intégrés (configurés dans config.py)

|                Modèle               |  VRAM  |   Type    |           Cas d'usage              |
|-------------------------------------|--------|-----------|----------------------------------- |
| `deepseek-coder:6.7b-instruct-q8_0` | ~4GB   | code      | Bug, SQL, API, scripts             |
| `llama3.1:8b-instruct-q4_K_M`       | ~4GB   | reasoning | Analyse, explication, comparaison  |
| `mistral:latest`                    | ~4GB   | chat      | Questions courtes, conversation    |
| `gemma3:4b`                         | ~3GB   | general   | Fallback général                   |
| `minicpm-v:8b-2.6-q2_K`             | ~4GB   | vision    | Image, photo, description visuelle |
| `nomic-embed-text`                  | ~270MB | embedding | Routing sémantique interne         |
 
 ---

## Architecture des services

|    Service	|  Port	 |                Rôle                 |          URL            |
|---------------|--------|-------------------------------------|------------------------ |
| llm-router	| 5000	 | API de routage intelligent (FastAPI)| http://localhost:5000   |
| ollama	| 11434	 | Serveur de modèles (GPU activé)     | http://localhost:11434  |
| open-webui	| 3000	 | Interface Web + RAG                 | http://localhost:3000   |

---

## Architecture des fichiers

| Fichier     |                      Rôle                                |
|-------------|----------------------------------------------------------|
| `config.py` | **Source de vérité unique** : modèles, URL, mots-clés    |
| `models.py` | Embeddings via `nomic-embed-text` + vecteurs précalculés |
| `router.py` | Logique principale : routing, stream, endpoints          |
| `main.py`   | Point d'entrée unique (`from router import app`)         |
| `cache.py`  | Cache in-memory (→ Redis sur NAS)                        |
| `memory.py` | Historique de sessions (→ Redis sur NAS)                 |
| `logs.py`   | Logging structuré de chaque requête/routing              |

---

## Installation rapide

```bash
# 1. Cloner le dépôt
git clone https://github.com/RemyDaubenfeld/llm-router.git
cd llm-router

# 2. Si un Ollama système tourne, l'arrêter
sudo systemctl stop ollama
sudo systemctl disable ollama

# 3. Lancer tous les services
docker compose up -d --build

# 4. Pull des modèles recommandés  (À faire une seule fois après le premier lancement)
docker compose exec ollama ollama pull deepseek-coder:6.7b-instruct-q8_0
docker compose exec ollama ollama pull llama3.1:8b-instruct-q4_K_M
docker compose exec ollama ollama pull mistral:latest
docker compose exec ollama ollama pull gemma3:4b
docker compose exec ollama ollama pull minicpm-v:8b-2.6-q2_K
docker compose exec ollama ollama pull nomic-embed-text

# Autres commandes utiles :
docker compose exec ollama ollama list        # lister les modèles
docker compose exec ollama ollama ps          # modèles en cours d'exécution
docker compose exec ollama ollama rm <modèle> # supprimer un modèle
```

---

## Utilisation

# 1.OpenWebUI (interface graphique)

**Connexions → API compatibles OpenAI**
-> Paramètres admin → Connexions → API compatibles OpenAI :
- URL → `http://llm-router:5000/v1`
- Clé API → `ia-local`

**Connexions → API Ollama** (pour les embeddings RAG)
-> Paramètres admin → Connexions → API Ollama :
- URL → `http://ollama:11434`

> Ces URLs utilisent les noms des services Docker — ne pas mettre `localhost` qui ne fonctionnerait pas depuis l'intérieur des containers.

**Sélection du modèle dans OpenWebUI**
Le modèle sélectionné dans OpenWebUI est un **pass-through** — peu importe lequel tu choisis, c'est le router qui décide du vrai modèle utilisé selon le contenu du prompt.

# 2.OpenCode (agent IA en terminal)

Voir le fichier **OpenCode-guide.md** intégré au projet.

# 3.Appel direct à l’API

```bash
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Écris une fonction fibonacci en Python"}],"stream":false}'
```

---

## Personnalisation du routage

Éditez **config.py** pour :
- Modifier les boost de mots‑clés (keywords)
- Ajuster les poids (weight)
- Ajouter / supprimer des modèles

---

## Routing

Pour chaque prompt :
1. **Embedding sémantique** (cosine similarity) via `nomic-embed-text` dans Ollama
2. **Boost mots-clés** (+0.3) définis par modèle dans `config.py`
3. **Bonus vitesse** (+0.05) pour les prompts courts sur les modèles rapides

Pour voir quel modèle est choisi en temps réel :

```bash
docker compose logs -f llm-router
```

---

## Endpoints du router

- `GET  /health` — état du serveur + taille du cache
- `GET  /v1/models` — liste des modèles (compatibilité OpenAI)
- `POST /v1/chat/completions` — endpoint principal (stream ou sync)

---

## Base de connaissances (RAG)

OpenWebUI intègre un système RAG natif qui fonctionne directement avec `nomic-embed-text`.
Les fichiers sont découpés en chunks, transformés en embeddings et récupérés automatiquement selon le prompt.

**Configuration embeddings** (une seule fois)
-> Paramètres admin → Documents :
- Modèle d'embedding → `nomic-embed-text`
- URL → `http://ollama:11434`

**Créer une base de connaissances**
->Espace de travail → Connaissances → + Nouvelle base de connaissances

Uploade tes fichiers ou synchronise un dossier — OpenWebUI génère les embeddings automatiquement. Pour un projet qui évolue, utilise **Téléverser un dossier** pour que les modifications soient prises en compte.

**Utiliser la base dans une conversation**
Dans le chat, tape `#` puis le nom de ta base. OpenWebUI récupère les passages pertinents et les injecte dans le contexte avant d'envoyer au router.

**Flux complet**
```
Question sur ton projet
        ↓
OpenWebUI cherche les passages pertinents (nomic-embed-text)
        ↓
Injecte ces passages dans le prompt
        ↓
Router → choisit le bon modèle (deepseek, llama, mistral...)
        ↓
Réponse contextualisée
```

> Tout reste 100% local. Le router n'a pas besoin de modification.

---

## Bonnes pratiques

- Utiliser un modèle dédié par tâche — le router s'en charge automatiquement
- Ne pas donner trop de contexte d'un coup — travailler par petites tâches
- Pour du code → laisser le router choisir (deepseek sera sélectionné)
- Pour de l'analyse → laisser le router choisir (llama sera sélectionné)
- Sauvegarder régulièrement le volume Docker `open-webui` (historique, comptes)

---

## Volumes Docker

```bash
docker volume ls                           # lister les volumes
docker volume rm llm_router_open-webui     # supprimer (efface historique et comptes)
```
> Supprimer un container ne supprime pas ses données — les volumes sont indépendants.
 
**Sauvegarder le volume OpenWebUI**
```bash
docker run --rm -v llm_router_open-webui:/data -v $(pwd):/backup alpine \
  tar czf /backup/open-webui-backup.tar.gz /data
```

---

## Démarrage automatique

Tous les services redémarrent automatiquement grâce à `restart: unless-stopped`.

Pour que Docker démarre au boot :
```bash
sudo systemctl enable docker
```

---

## Variables d'environnement

|   Variable   |                Défaut              |          Description           |
|--------------|------------------------------------|--------------------------------|
| `OLLAMA_URL` | `http://ollama:11434/api/generate` | URL d'Ollama (auto via Docker) |

---

## Optimisations GPU (pour cette configuration)

Dans docker-compose.yml, le service ollama inclut déjà :

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

Ces variables assurent un offloading partiel sur GPU et une meilleure gestion de la mémoire.

---

## Migration Redis (NAS)

Les commentaires dans `cache.py` et `memory.py` indiquent exactement les lignes à remplacer :

```bash
pip install redis
```

---

## Licence

MIT - libre d'utiliser, modifier et distribuer.

---

## Remerciements

- **Ollama** pour l’exécution locale des modèles
- **OpenWebUI** pour l’interface et le RAG
- **OpenCode** pour l’agent terminal
- **FastAPI** pour la performance et la simplicité