
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
=======
There are various types of memory 
using python to create a working memory which will take care of current memory
using sqlite to take care of episodal memory fact 
wont giving context will cost lot of tokens ?
we are not content stuffing (dumping all memory all at once)
we are emphasizing on selective retrieval (3-5 relevant memories for their specific prompt)

lets go through three patterns:
1)Pre Prompt Injection - the user ai query do u know about this msg and then sent 3 relative memory to the prompt

2)Confidence filtering - if a memory is in the ai bus but what if its too old then there comes the confidence score 


3)Tiered Injection- there are different type of memories like working mrmory,episodic memory,semantic memory if we inject all three at once that will lead to wastage of tokens




