> **[🇬🇧 English](OpenCode-guide-en.md) | [🇫🇷 Français](OpenCode-guide-fr.md)**

# OpenCode — User Guide

AI coding agent in the terminal, connected to local Ollama.

---

## Installation

```bash
npm install -g opencode-ai@latest
```

Config for local Ollama (`~/.config/opencode/config.json`) :

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

## Launch

```bash
cd /your/project
opencode
```

On first launch in a project, type `/init` — OpenCode analyzes all files and generates an `AGENTS.md` context file. It will be more relevant in its suggestions afterwards.

---

## The two modes (Tab to switch)

**Plan (read-only)**
- Analyzes code, asks questions, thinks
- Does not modify any files
- Ideal for: understanding a codebase, planning a feature, debugging

**Build (active modifications)**
- Reads and modifies files directly
- Proposes each change as a diff to validate
- Ideal for: implementing, refactoring, fixing bugs

> Best practice: always start in **Plan** to validate the approach, then switch to **Build** to apply.

---

## Main commands

| Command  |              Description                |
|----------|-----------------------------------------|
| `/init`  | Analyze the project and generate AGENTS.md |
| `/share` | Generate a sharing link for the session |
| `/clear` | Clear conversation history              |
| `/model` | Change model on the fly                 |
| `Tab`    | Switch between Plan and Build           |
| `Ctrl+C` | Quit                                    |

---

## Effective prompt examples

**Debugging**
```
This code returns a KeyError on line 42 of cache.py.
Analyze and fix it.
```

**Implementing a feature**
```
Add a function in memory.py that removes sessions
inactive for more than 24 hours.
```

**Refactoring**
```
The router.py file does too many things. Propose a split
into smaller functions and apply it.
```

**Understanding a project**
```
Explain the architecture of this project and how the files
interact with each other.
```

**Generating tests**
```
Generate unit tests for the select_model function in router.py.
```

---

## OpenCode vs OpenWebUI — when to use which?

|           Task            | Recommended tool |
|---------------------------|------------------|
| Write / modify code       | **OpenCode**     |
| Debug in a project        | **OpenCode**     |
| Refactor files            | **OpenCode**     |
| General questions         | **OpenWebUI**    |
| Document analysis         | **OpenWebUI**    |
| Conversation / writing    | **OpenWebUI**    |
| Vision / images           | **OpenWebUI**    |

---

## Context window (right column)

### Context: X tokens — X% used — $0.00 spent

This is the model's **context window** — the amount of information it can keep in memory at once. Each file read and each exchange consumes tokens.

- **$0.00 spent**: normal in local mode, it would show a real cost with Claude or GPT
- Below **70%**: everything is fine
- Between **70% and 90%**: responses may become less coherent
- Above **90%**: type `/clear` to start fresh — the model starts "forgetting" the beginning

> That's why it's better to work in small tasks. Reading a large project all at once quickly consumes the context.

### LSP — LSPs will activate as files are read

The **Language Server Protocol** allows OpenCode to connect to your editor's analysis tools (VSCode, etc.) for a finer understanding of the code: types, errors, references. It activates automatically as files are read — nothing to configure.

---

## Best practices

- **Work in small tasks** — one problem at a time, not the whole project at once
- **Always review diffs** before validating in Build mode
- **Use /init** in each new project to provide context
- **Commit before** letting OpenCode modify files — makes rollback easier
- **Plan mode first** for important changes, then Build

---

## Changing the model

To use llama instead of deepseek temporarily:

```bash
# Inside an opencode session
/model ollama/llama3.1:8b-instruct-q4_K_M
```

Or modify `~/.config/opencode/config.json` to change the default.