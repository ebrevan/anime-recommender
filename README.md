# anime-recommender

A small CLI chatbot that recommends anime series based on your mood / likes, powered by Claude via LangChain.

## Setup

```bash
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# then edit .env and paste your Anthropic API key
```

## Run

```bash
python agent.py
```

Slash commands inside the REPL:
- `/reset` — clear conversation context
- `/quit` (or `/exit`, Ctrl+D) — exit
