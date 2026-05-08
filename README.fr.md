> **[🇬🇧 English](README.md) | [🇫🇷 Français](README.fr.md)**

# LLM Router : Routeur intelligent pour modèles LLM locaux

![Docker](https://img.shields.io/badge/docker-compose-2496ED)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![License](https://img.shields.io/badge/license-MIT-green)

**LLM Router** est un serveur API qui analyse automatiquement le contenu de vos prompts et sélectionne le modèle le plus adapté parmi vos modèles locaux.
Plus besoin de choisir manuellement entre code, raisonnement, chat ou vision — le router decide pour vous.

```
┌─────────────┐    ┌──────────────┐    ┌────────────┐    ┌──────────────┐
│  Utilisateur │───▶│  OpenWebUI   │───▶│ LLM Router │───▶│   Ollama     │
│             │    │   (:3000)    │    │   (:5000)   │    │  (:11434)    │
└─────────────┘    └──────────────┘    └──────┬─────┘    └──────┬───────┘
                                             │                   │
                                    config / cache / logs ───────┘
```

---

## Fonctionnalités

✅ **Routing sémantique intelligent** — Embeddings cosine similarity + boost par mots-clés + bonus vitesse

✅ **Cache intelligent** — Réponses en mémoire (prêt pour Redis sur NAS)

✅ **Mémoire de session** — Historique des conversations

✅ **Logging structuré** — Trace de chaque requête et décision de routage

✅ **Compatible OpenAI API** — OpenWebUI, Continue, et tout client OpenAI

✅ **Support GPU** — Acceleration NVIDIA via container toolkit

✅ **Docker Compose** — Déploiement en une commande

---

## Architecture des services

|    Service	|  Port	 |                Rôle                 |          URL            |
|-------------|--------|-------------------------------------|------------------------ |
| llm-router	| 5000	 | API de routage intelligent (FastAPI)| http://localhost:5000   |
| ollama	    | 11434	 | Serveur de modèles (GPU activé)     | http://localhost:11434  |
| open-webui	| 3000	 | Interface Web + RAG                 | http://localhost:3000   |

---

## Architecture des fichiers

| Fichier | Rôle |
|---------|------|
| `config.py` | **Source de vérité** — modèles, URLs, mots-clés de boost, poids |
| `models.py` | Embeddings + vecteurs de référence précalculés |
| `router.py` | Logique principale — routing, streaming, endpoints |
| `main.py` | Point d'entrée FastAPI (`from router import app`) |
| `cache.py` | Cache in-memory LRU (→ Redis sur NAS) |
| `memory.py` | Historique des sessions (→ Redis sur NAS) |
| `logs.py` | Logging JSON de chaque requête et routage |
| `docker-compose.yml` | Orchestration des services (router, ollama, openwebui) |

---

## Installation

### 1. Prérequis

- [Docker](https://docs.docker.com/engine/install/) + Docker Compose
- GPU Nvidia : installer [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

**Vérifier l'accès GPU**

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Sans GPU Nvidia : supprimez le bloc `deploy` dans `docker-compose.yml` (fonctionnement CPU possible).

### 2. Lancer les services

```bash
# Cloner le projet
git clone https://github.com/RemyDaubenfeld/llm-router.git
cd llm-router

# Arrêter Ollama système si présent
sudo systemctl stop ollama
sudo systemctl disable ollama

# Lancer Docker Compose
docker compose up -d --build
```

### 3. Télécharger les modèles

Tous les modèles sont stockés dans Ollama. Pour en ajouter un :

```bash
docker compose exec ollama ollama pull <nom_du_modele>
```

Pour trouver des modèles : [Ollama](https://ollama.com/search)

> Le premier lancement peut prendre 10-30 minutes selon votre connexion et votre GPU.


**Modèle recommandé pour commencer**

Si vous débutez, installez d'abord `nomic-embed-text` (utilisé pour le routing) :

```bash
docker compose exec ollama ollama pull nomic-embed-text
```

### Commandes utiles

```bash
docker compose exec ollama ollama list        # Lister les modèles
docker compose exec ollama ollama ps          # Modèles actifs
docker compose logs -f llm-router             # Logs du router en temps réel
docker compose restart llm-router             # Redémarrer après modification de config.py
docker compose pull                           # Mettre à jour les images
```

---

### Utilisation

OpenWebUI peut être configuré de deux manières différentes — **ne pas activer les deux en même temps**.

### Solution 1 : Utiliser le router (recommandé)

Le router analyse automatiquement votre prompt et choisit le modèle le plus adapté.

**Connexions → API compatibles OpenAI**
-> Paramètres admin → Connexions → API compatibles OpenAI :
- URL → `http://llm-router:5000/v1`
- Clé API → `ia-local`

> Le modèle sélectionné dans OpenWebUI est un **pass-through** — peu importe celui que vous choisissez, c'est le router qui décide du modèle réel selon le contenu du prompt. Sélectionnez n'importe quel modèle disponible uniquement pour activer la conversation.

### Solution 2 : Utiliser Ollama directement

Pas de routage automatique — vous choisissez vous-même le modèle à chaque conversation.

**Connexions → API Ollama**
-> Paramètres admin → Connexions → API Ollama :
- URL → `http://ollama:11434`

> Ces URLs utilisent les noms des services Docker — ne pas mettre `localhost` qui ne fonctionnerait pas depuis l'intérieur des containers.

---

### Modèle d'embedding pour le RAG

Si vous utilisez une base de connaissances, installez d'abord le modèle d'embedding :

```bash
docker compose exec ollama ollama pull nomic-embed-text
```

---

### Appel direct à l’API

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
1. **Embedding sémantique** (Similarité cosinus) via `nomic-embed-text` dans Ollama
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

Uploadez les fichiers ou synchronisez un dossier — OpenWebUI génère les embeddings automatiquement. Pour un projet qui évolue, utilisez **Téléverser un dossier** pour que les modifications soient prises en compte.

**Utiliser la base dans une conversation**
Dans le chat, tape `#` puis le nom de ta base. OpenWebUI récupère les passages pertinents et les injecte dans le contexte avant d'envoyer au router.

**Flux complet**
```
Question sur un projet
        ↓
OpenWebUI cherche les passages pertinents (nomic-embed-text)
        ↓
Injecte ces passages dans le prompt
        ↓
Router → choisit le bon modèle parmi ceux affiché dans `config.py`
        ↓
Réponse contextualisée
```

> Tout reste 100% local. Le router n'a pas besoin de modification.

---

## FAQ / Dépannage

**Le modèle ne répond pas ou le router retourne une erreur 500**
- Vérifiez que le modèle est bien téléchargé : `docker compose exec ollama ollama list`
- Vérifiez les logs : `docker compose logs llm-router`

**Comment savoir quel modèle a été sélectionné ?**
```bash
docker compose logs -f llm-router | grep "Selected model"
```

**Comment modifier le routage (mots-clés, poids) ?**
Éditez `config.py`, puis redémarrez le router :
```bash
docker compose restart llm-router
```

**Comment ajouter un nouveau modèle ?**
1. Ajoutez-le dans `config.py` (nom, type, mots-clés, poids)
2. Téléchargez-le : `docker compose exec ollama ollama pull <nom_du_modèle>`
3. Redémarrez le router : `docker compose restart llm-router`

**Le GPU n'est pas utilisé**
- Vérifiez que `nvidia-container-toolkit` est installé
- Exécutez : `sudo nvidia-ctk runtime configure --runtime=docker`
- Redémarrez Docker : `sudo systemctl restart docker`
- Vérifiez : `docker run --rm --gpus all nvidia/cuda:12.0-base-ubuntu22.04 nvidia-smi`

**Récupérer l'espace disque après suppression de modèles**
```bash
docker compose exec ollama rm -rf /root/.ollama/models/
docker compose down -v  # Supprime aussi les volumes
```

**Comment réinitialiser complètement ?**
```bash
docker compose down -v --rmi all
docker system prune -a
```

---

## Bonnes pratiques

- Utiliser un modèle dédié par tâche — le router s'en charge automatiquement
- Ne pas donner trop de contexte d'un coup — travailler par petites tâches
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

## Migration Redis (NAS ou autre serveur)

Les commentaires dans `cache.py` et `memory.py` indiquent exactement les lignes à remplacer :

```bash
pip install redis
```

---

## Licence

MIT - libre d'utiliser, modifier et distribuer.

---

## Remerciements

- **Ollama** pour l'exécution locale des modèles
- **OpenWebUI** pour l'interface et le RAG
- **FastAPI** pour la performance et la simplicité