# OpenCode — Guide d'utilisation

Agent de coding IA dans le terminal, connecté à ton Ollama local.

---

## Installation

```bash
npm install -g opencode-ai@latest
```

Config pour Ollama local (`~/.config/opencode/config.json`) :

```bash
cat > ~/.config/opencode/config.json << 'EOF'
{
  "model": "ollama/deepseek-coder:6.7b-instruct-q8_0",
  "providers": {
    "ollama": {
      "url": "http://localhost:11434"
    }
  }
}
EOF
```

---

## Lancement

```bash
cd /ton/projet
opencode
```

Au premier lancement dans un projet, tape `/init` — OpenCode analyse
tous les fichiers et génère un fichier `AGENTS.md` de contexte.
Il sera plus pertinent dans ses suggestions ensuite.

---

## Les deux modes (Tab pour switcher)

### Plan (lecture seule)
- Analyse le code, pose des questions, réfléchit
- Ne modifie aucun fichier
- Idéal pour : comprendre une base de code, planifier une feature, débugger

### Build (modifications actives)
- Lit et modifie les fichiers directement
- Propose chaque changement sous forme de diff à valider
- Idéal pour : implémenter, refactoriser, corriger des bugs

> Bonne pratique : commence toujours en **Plan** pour valider l'approche,
> puis passe en **Build** pour appliquer.

---

## Commandes principales

| Commande |               Description               |
|----------|-----------------------------------------|
| `/init`  | Analyse le projet et génère AGENTS.md   |
| `/share` | Génère un lien de partage de la session |
| `/clear` | Efface l'historique de la conversation  |
| `/model` | Changer de modèle à la volée            |
| `Tab`    | Switcher entre Plan et Build            |
| `Ctrl+C` | Quitter                                 |

---

## Exemples de prompts efficaces

**Débugger**
```
Ce code retourne une erreur KeyError sur la ligne 42 de cache.py.
Analyse et corrige.
```

**Implémenter une feature**
```
Ajoute une fonction dans memory.py qui supprime les sessions
inactives depuis plus de 24h.
```

**Refactoriser**
```
Le fichier router.py fait trop de choses. Propose un découpage
en fonctions plus petites et applique-le.
```

**Comprendre un projet**
```
Explique-moi l'architecture de ce projet et comment les fichiers
interagissent entre eux.
```

**Générer des tests**
```
Génère des tests unitaires pour la fonction select_model dans router.py.
```

---

## OpenCode vs OpenWebUI — quand utiliser quoi ?

|           Tâche           | Outil recommandé |
|---------------------------|------------------|
| Écrire / modifier du code | **OpenCode**     |
| Débugger dans un projet   | **OpenCode**     |
| Refactoriser des fichiers | **OpenCode**     |
| Questions générales       | **OpenWebUI**    |
| Analyse de documents      | **OpenWebUI**    |
| Conversation / rédaction  | **OpenWebUI**    |
| Vision / images           | **OpenWebUI**    |

---

## Bonnes pratiques

- **Travailler par petites tâches** — un problème à la fois, pas tout le projet d'un coup
- **Toujours vérifier les diffs** avant de valider en mode Build
- **Utiliser /init** dans chaque nouveau projet pour donner du contexte
- **Commiter avant** de laisser OpenCode modifier des fichiers — facilite le rollback
- **Mode Plan d'abord** pour les changements importants, Build ensuite

---

## Changer de modèle

Pour utiliser llama à la place de deepseek ponctuellement :

```bash
# Dans la session opencode
/model ollama/llama3.1:8b-instruct-q4_K_M
```

Ou modifier `~/.config/opencode/config.json` pour changer le défaut.

---

## Lexique pour l'interface en anglais
L'interface du terminal est en anglais, mais vous pouvez parler à l'IA en français. Voici les termes clés à retenir :

|   Terme anglais   |    Signification   |                    Action                           |
|-------------------|--------------------|-----------------------------------------------------|
| Plan mode         | Mode planification | L'IA analyse sans modifier.                         |
| Build mode        | Mode construction  | L'IA écrit ou modifie le code.                      |
| Approve / Accept  | Accepter           | Valide les changements (souvent touche y).          |
| Reject / Discard  | Refuser            | Annule les changements proposés (souvent touche n). |
| Context           | Contexte           | Pour ajouter des fichiers à la lecture de l'IA.     |
| Undo              | Annuler            | Revient à l'état précédent du fichier.              |

Astuce : Si l'IA vous répond en anglais, dites-lui simplement : "Réponds-moi dorénavant uniquement en français".

