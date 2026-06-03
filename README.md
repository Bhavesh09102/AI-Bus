# AI Memory Bus

A full-stack local application where every AI shares one persistent memory layer. What one AI learns, all others know instantly.

## Setup

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
python app.py
# Runs on http://localhost:5000

# 2. Frontend
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173

# 3. Ollama (free local AI — no account needed)
# Download from https://ollama.com/download
ollama pull llama3
ollama serve
# Runs on http://localhost:11434

# 4. Open http://localhost:5173
# Ollama is ready immediately — no setup needed
# For cloud AIs: click any locked card and paste your API key
```

## Architecture

- **Working memory** — RAM (OrderedDict + heapq LRU/TTL)
- **Episodic memory** — SQLite timestamped events
- **Semantic memory** — ChromaDB + sentence-transformers (all-MiniLM-L6-v2)

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ping` | Health check |
| POST | `/chat` | Main chat with memory injection |
| POST | `/memory/write` | Write to working/episodic/semantic |
| GET | `/memory/recall` | Recall by type |
| GET | `/memory/context` | All working memory keys |
| DELETE | `/memory/<id>` | Delete memory |
| POST | `/memory/flush` | Clear working memory |
| GET | `/info` | Stats |
