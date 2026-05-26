# anime-recommender

A small CLI chatbot that recommends anime series based on your mood / likes, powered by Claude via LangChain.

## Setup

```bash
source venv/bin/activate
pip install -r requirements.txt
cat > .env <<'EOF'
ANTHROPIC_API_KEY=your_anthropic_key
DD_API_KEY=your_datadog_api_key   # optional, enables LLM Obs
DD_SITE=datadoghq.com             # optional, defaults to datadoghq.com
EOF
```

## Run

```bash
python agent.py
```

Slash commands inside the REPL:
- `/reset` — clear conversation context
- `/quit` (or `/exit`, Ctrl+D) — exit
