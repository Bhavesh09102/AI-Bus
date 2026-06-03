"""
pydantic_fastapi_basics.py
Week 2 — Deep dive reference

Sections:
  PART 1 — Pydantic alone (no FastAPI)
  PART 2 — FastAPI basics (routes, requests, responses)
  PART 3 — Pydantic + FastAPI together
  PART 4 — Your Memory Bus endpoints (real project code)

Run each part independently to understand it before combining.
"""


# ═══════════════════════════════════════════════════════════════════
# PART 1 — PYDANTIC ALONE
# Understand this before touching FastAPI.
# ═══════════════════════════════════════════════════════════════════

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# ── 1.1 The simplest model ─────────────────────────────────────────

class MemoryWrite(BaseModel):
    # These are fields. Each has a type annotation.
    # Pydantic enforces these types on every input.
    type: str
    content: str
    confidence: float
    ttl: int


# Creating a model instance — Pydantic validates on creation
m = MemoryWrite(
    type="working",
    content="user is working on auth.py",
    confidence=0.9,
    ttl=3600
)
print(m.type)        # "working"
print(m.confidence)  # 0.9
print(m.model_dump()) # converts back to plain dict


# ── 1.2 Type coercion — Pydantic tries to convert before rejecting ─

# If you send confidence as a string "0.9", Pydantic converts it to
# float 0.9 automatically. This is called coercion.
m2 = MemoryWrite(
    type="episodic",
    content="Fixed login bug",
    confidence="0.85",  # string — Pydantic coerces to float 0.85
    ttl="3600"          # string — Pydantic coerces to int 3600
)
print(m2.confidence)  # 0.85 (float, not string)


# ── 1.3 Optional fields with defaults ──────────────────────────────

class MemoryWriteV2(BaseModel):
    type: str
    content: str
    confidence: float = 1.0          # default value — field is optional
    ttl: Optional[int] = None        # can be int OR None
    tags: list[str] = []             # default empty list
    source: str = "unknown"          # which app is writing


# Only required fields needed — rest use defaults
m3 = MemoryWriteV2(type="semantic", content="User prefers Python")
print(m3.confidence)  # 1.0  (default)
print(m3.ttl)         # None (default)
print(m3.tags)        # []   (default)


# ── 1.4 Field() — add constraints and documentation ────────────────

class MemoryWriteV3(BaseModel):
    type: str = Field(
        ...,                          # ... means REQUIRED (no default)
        description="Memory type: working | episodic | semantic"
    )
    content: str = Field(
        ...,
        min_length=1,                 # content cannot be empty string
        max_length=10000
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,                       # ge = greater than or equal to
        le=1.0                        # le = less than or equal to
    )
    ttl: Optional[int] = Field(
        default=None,
        gt=0                          # gt = greater than (must be positive)
    )


# ── 1.5 Custom validators — your own logic ─────────────────────────

VALID_TYPES = {"working", "episodic", "semantic", "procedural"}

class MemoryWriteV4(BaseModel):
    type: str
    content: str
    ttl: Optional[int] = None

    @field_validator("type")
    @classmethod
    def type_must_be_valid(cls, v):
        # v is the incoming value
        if v not in VALID_TYPES:
            raise ValueError(f"type must be one of {VALID_TYPES}, got '{v}'")
        return v  # return the validated value

    @field_validator("ttl")
    @classmethod
    def ttl_only_for_working(cls, v, info):
        # info.data contains already-validated fields
        if v is not None and info.data.get("type") != "working":
            raise ValueError("ttl is only valid for type=working")
        return v


# ── 1.6 What happens when validation fails ─────────────────────────

from pydantic import ValidationError

try:
    bad = MemoryWriteV4(type="invalid_type", content="test")
except ValidationError as e:
    # Pydantic gives you a structured error — not a cryptic crash
    print(e)
    # Output:
    # 1 validation error for MemoryWriteV4
    # type
    #   Value error, type must be one of {...}, got 'invalid_type'


# ── 1.7 Response models — what you send BACK ───────────────────────
# Pydantic isn't just for incoming data. Define response shapes too.

class MemoryWriteResponse(BaseModel):
    status: str               # "ok" or "error"
    id: str                   # "mem_a1b2c3"
    type: str
    written_at: datetime      # Pydantic serializes datetime to ISO string


# ═══════════════════════════════════════════════════════════════════
# PART 2 — FASTAPI BASICS
# Routes, HTTP verbs, path params, query params, request body
# ═══════════════════════════════════════════════════════════════════

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

app = FastAPI(
    title="AI Memory Bus",
    description="Shared memory layer for local AI applications",
    version="1.0.0"
)

# ── 2.1 The simplest route ─────────────────────────────────────────

@app.get("/ping")
async def ping():
    # GET /ping → {"status": "ok"}
    # async def means FastAPI can handle other requests while this
    # one is running. For a simple return like this it doesn't matter,
    # but the pattern is consistent and correct.
    return {"status": "ok"}


# ── 2.2 Path parameters — part of the URL itself ───────────────────

@app.get("/memory/{memory_id}")
async def get_memory(memory_id: str):
    # GET /memory/mem_a1b2c3
    # memory_id is extracted from the URL path
    # FastAPI validates: if memory_id is missing, 404 automatically
    return {"id": memory_id, "content": "example"}


# ── 2.3 Query parameters — after the ? in the URL ──────────────────

@app.get("/memory/recall")
async def recall_memory(
    type: str,                         # required query param
    q: Optional[str] = None,           # optional query param
    top_k: int = 5,                    # optional with default
    since: Optional[str] = None,       # for episodic date filter
    until: Optional[str] = None
):
    # GET /memory/recall?type=semantic&q=python+preference&top_k=3
    # FastAPI reads these from the URL query string automatically
    # You don't write any parsing code — it's all declarative
    return {
        "type": type,
        "query": q,
        "top_k": top_k
    }


# ── 2.4 Request body — JSON payload in POST requests ───────────────

@app.post("/memory/write")
async def write_memory(payload: MemoryWriteV4):
    # The payload parameter tells FastAPI to:
    #   1. Read the JSON body from the request
    #   2. Pass it through MemoryWriteV4 (Pydantic validates it)
    #   3. If invalid → automatically return 422 with error details
    #   4. If valid → your function runs with a clean, typed object

    # You access fields like a normal Python object — no dict lookups
    memory_type = payload.type
    content = payload.content

    # Do the actual work here (we'll wire stores in later)
    memory_id = "mem_example123"

    return {"status": "ok", "id": memory_id, "type": memory_type}


# ── 2.5 HTTP errors — how to return 404, 400, etc. ─────────────────

@app.delete("/memory/{memory_id}")
async def forget_memory(memory_id: str):
    # Simulate a lookup
    found = False  # in real code: check your store

    if not found:
        # HTTPException tells FastAPI to return the right HTTP status
        # with a JSON body: {"detail": "Memory not found"}
        raise HTTPException(status_code=404, detail="Memory not found")

    return {"status": "deleted", "id": memory_id}


# ── 2.6 async vs sync — when does it matter? ───────────────────────

# RULE: if your function touches disk, network, or a database → async def + await
# RULE: if your function only touches RAM → async def is fine but await isn't needed

# sync — fine for pure RAM operations
@app.get("/memory/context")
async def get_context():
    # working_memory.keys() only touches RAM — no await needed
    # but we still use async def for consistency
    keys = ["current_task", "active_file"]  # placeholder
    return {"keys": keys}


# async with await — for disk operations
@app.post("/memory/write/episodic")
async def write_episodic(payload: MemoryWriteV4):
    # await tells Python: "start this, let other requests run,
    # come back when it's done"
    # await episodic_store.write(payload.content)  # disk I/O
    return {"status": "ok"}


# ── 2.7 The /docs page — free and automatic ────────────────────────
# Run your server and visit http://localhost:8000/docs
# FastAPI generates a full interactive API explorer from your code.
# Every route, every parameter, every model is documented automatically.
# This is Swagger UI — built in, zero config.
# You can test your endpoints directly from the browser.


# ═══════════════════════════════════════════════════════════════════
# PART 3 — PYDANTIC + FASTAPI TOGETHER
# The full pattern you'll use in your project
# ═══════════════════════════════════════════════════════════════════

# ── 3.1 Request model → route → response model ─────────────────────

class WriteRequest(BaseModel):
    """What comes IN"""
    type: str = Field(..., description="working | episodic | semantic")
    content: str = Field(..., min_length=1)
    source: str = Field(default="unknown")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    ttl: Optional[int] = Field(default=None, gt=0)
    tags: list[str] = []

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        valid = {"working", "episodic", "semantic", "procedural"}
        if v not in valid:
            raise ValueError(f"Invalid type '{v}'. Must be one of {valid}")
        return v


class WriteResponse(BaseModel):
    """What goes OUT"""
    status: str
    id: str
    type: str


# Route uses both — FastAPI handles the wiring
@app.post("/v2/memory/write", response_model=WriteResponse)
async def write_memory_v2(payload: WriteRequest) -> WriteResponse:
    # payload is guaranteed valid here — Pydantic already checked it
    memory_id = f"mem_{hash(payload.content) % 100000:05d}"
    return WriteResponse(
        status="ok",
        id=memory_id,
        type=payload.type
    )


# ── 3.2 Query param validation with Query() ─────────────────────────

@app.get("/v2/memory/recall")
async def recall_v2(
    type: str = Query(..., description="Memory type to search"),
    q: Optional[str] = Query(None, min_length=1),
    top_k: int = Query(default=5, ge=1, le=50),
    since: Optional[str] = Query(None, description="ISO date e.g. 2026-05-19"),
    until: Optional[str] = Query(None, description="ISO date e.g. 2026-05-21")
):
    # Query() works exactly like Field() but for URL parameters
    # FastAPI validates: top_k must be between 1 and 50
    # If top_k=0 is passed → 422 Unprocessable Entity, automatic
    return {"type": type, "q": q, "top_k": top_k}


# ═══════════════════════════════════════════════════════════════════
# PART 4 — YOUR ACTUAL PROJECT CODE
# Wire WorkingMemory + SQLite into a real running server
# Save this as main.py and run: uvicorn main:app --reload
# ═══════════════════════════════════════════════════════════════════

import time
import sqlite3
import uuid

# -- Import your week 1 class (assumes working_memory.py is in same folder)
# from working_memory import WorkingMemory

# For this file to be self-contained, we inline a minimal version:
import heapq
from collections import OrderedDict

class WorkingMemory:
    def __init__(self, max_size=500):
        self._store = OrderedDict()
        self._ttl_heap = []
        self._max_size = max_size

    def set(self, key, value, ttl):
        expire_at = time.time() + ttl
        self._store[key] = (value, expire_at)
        self._store.move_to_end(key)
        heapq.heappush(self._ttl_heap, (expire_at, key))
        self._evict_if_full()

    def get(self, key):
        if key not in self._store:
            return None
        value, expire_at = self._store[key]
        if time.time() > expire_at:
            del self._store[key]
            return None
        self._store.move_to_end(key)
        return value

    def all_keys(self):
        now = time.time()
        return {
            k: v for k, (v, exp) in self._store.items() if now <= exp
        }

    def delete(self, key):
        return bool(self._store.pop(key, None))

    def flush(self):
        self._store.clear()
        self._ttl_heap.clear()

    def _evict_if_full(self):
        while len(self._store) > self._max_size:
            self._store.popitem(last=False)

    def _evict_expired(self):
        now = time.time()
        while self._ttl_heap and self._ttl_heap[0][0] <= now:
            exp, key = heapq.heappop(self._ttl_heap)
            if key in self._store and self._store[key][1] == exp:
                del self._store[key]


# -- Episodic store using SQLite (from your week 1 SQLite work)
class EpisodicStore:
    def __init__(self, db_path: str = "memory_bus.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS episodic_memory (
                id          TEXT PRIMARY KEY,
                content     TEXT NOT NULL,
                source      TEXT DEFAULT 'unknown',
                confidence  REAL DEFAULT 1.0,
                tags        TEXT DEFAULT '',
                written_at  TEXT NOT NULL
            )
        """)
        # Index on written_at for fast time-range queries — O(log n)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_written_at
            ON episodic_memory(written_at)
        """)
        self.conn.commit()

    def write(self, content: str, source: str, confidence: float, tags: list) -> str:
        memory_id = f"mem_{uuid.uuid4().hex[:8]}"
        written_at = datetime.utcnow().isoformat()
        self.conn.execute("""
            INSERT INTO episodic_memory (id, content, source, confidence, tags, written_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (memory_id, content, source, confidence, ",".join(tags), written_at))
        self.conn.commit()
        return memory_id

    def recall_by_range(self, since: str, until: str) -> list:
        cursor = self.conn.execute("""
            SELECT id, content, source, confidence, written_at
            FROM episodic_memory
            WHERE written_at BETWEEN ? AND ?
            ORDER BY written_at ASC
        """, (since, until))
        return [
            {"id": r[0], "content": r[1], "source": r[2],
             "confidence": r[3], "written_at": r[4]}
            for r in cursor.fetchall()
        ]

    def forget(self, memory_id: str) -> bool:
        cursor = self.conn.execute(
            "DELETE FROM episodic_memory WHERE id = ?", (memory_id,)
        )
        self.conn.commit()
        return cursor.rowcount > 0


# -- The actual FastAPI server
bus_app = FastAPI(title="AI Memory Bus", version="1.0.0")

# Single instances — shared across all requests
working_mem = WorkingMemory(max_size=500)
episodic_mem = EpisodicStore(db_path="memory_bus.db")


# -- Models for this server
class BusWriteRequest(BaseModel):
    type: str = Field(..., description="working | episodic | semantic")
    content: str = Field(..., min_length=1)
    source: str = "unknown"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    ttl: Optional[int] = Field(default=None, gt=0)
    tags: list[str] = []
    key: Optional[str] = None  # only for type=working

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v not in {"working", "episodic", "semantic", "procedural"}:
            raise ValueError(f"Invalid type: {v}")
        return v

    @field_validator("ttl")
    @classmethod
    def ttl_only_for_working(cls, v, info):
        if v is not None and info.data.get("type") != "working":
            raise ValueError("ttl is only valid for type=working")
        return v


# -- Endpoints

@bus_app.get("/ping")
async def ping():
    return {"status": "ok", "uptime_seconds": int(time.time())}


@bus_app.post("/memory/write")
async def write_memory(payload: BusWriteRequest):
    """
    Write a memory of any type.
    Router reads payload.type and dispatches to the right store.
    """

    if payload.type == "working":
        if payload.key is None:
            raise HTTPException(
                status_code=422,
                detail="key is required for type=working"
            )
        ttl = payload.ttl or 3600  # default 1 hour
        working_mem.set(payload.key, payload.content, ttl=ttl)
        return {"status": "ok", "id": payload.key, "type": "working"}

    elif payload.type == "episodic":
        # This touches disk — in real async code you'd await a proper
        # async DB driver. sqlite3 is sync, so we call it directly.
        # The async def still lets FastAPI stay responsive for RAM ops.
        memory_id = episodic_mem.write(
            content=payload.content,
            source=payload.source,
            confidence=payload.confidence,
            tags=payload.tags
        )
        return {"status": "ok", "id": memory_id, "type": "episodic"}

    elif payload.type in {"semantic", "procedural"}:
        # Week 3 will add these — return placeholder for now
        return {
            "status": "coming_in_week3",
            "type": payload.type,
            "message": "Semantic store added in week 3"
        }

    # Should never reach here — validator above catches invalid types
    raise HTTPException(status_code=400, detail="Unknown type")


@bus_app.get("/memory/context")
async def get_context():
    """Return all live working memory keys and values."""
    return working_mem.all_keys()


@bus_app.get("/memory/recall")
async def recall_memory(
    type: str = Query(...),
    q: Optional[str] = Query(None),
    since: Optional[str] = Query(None),
    until: Optional[str] = Query(None),
    top_k: int = Query(default=5, ge=1, le=50)
):
    """
    Recall memories. Behaviour depends on type:
      episodic → time range query (since/until)
      working  → all live keys (ignores q)
      semantic → semantic search by q (week 3)
    """
    if type == "episodic":
        if not since or not until:
            raise HTTPException(
                status_code=422,
                detail="since and until are required for type=episodic"
            )
        results = episodic_mem.recall_by_range(since, until)
        return {"results": results, "count": len(results)}

    elif type == "working":
        return {"results": working_mem.all_keys()}

    elif type == "semantic":
        return {"message": "Semantic search coming in week 3"}

    raise HTTPException(status_code=400, detail=f"Unknown type: {type}")


@bus_app.delete("/memory/{memory_id}")
async def forget_memory(memory_id: str):
    """Remove a memory by ID."""
    deleted = episodic_mem.forget(memory_id)
    if not deleted:
        # Also check working memory
        deleted = working_mem.delete(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "deleted", "id": memory_id}


@bus_app.post("/memory/flush")
async def flush_working():
    """Clear all working memory. Does not touch persistent stores."""
    working_mem.flush()
    return {"status": "ok", "message": "Working memory cleared"}


# ── How to run ───────────────────────────────────────────────────────
# Install: pip install fastapi uvicorn pydantic
# Run:     uvicorn pydantic_fastapi_basics:bus_app --reload --port 6400
# Docs:    http://localhost:6400/docs
#
# Test with curl:
#
# Write a working memory:
# curl -X POST http://localhost:6400/memory/write \
#   -H "Content-Type: application/json" \
#   -d '{"type":"working","key":"active_file","content":"auth.py","ttl":1800}'
#
# Write an episodic memory:
# curl -X POST http://localhost:6400/memory/write \
#   -H "Content-Type: application/json" \
#   -d '{"type":"episodic","content":"Fixed login bug","source":"vscode"}'
#
# Read all working memory:
# curl http://localhost:6400/memory/context
#
# Read episodic by date:
# curl "http://localhost:6400/memory/recall?type=episodic&since=2026-01-01&until=2026-12-31"
#
# Health check:
# curl http://localhost:6400/ping
