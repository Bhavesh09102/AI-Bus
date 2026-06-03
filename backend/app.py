import logging
import time
from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from flask_cors import CORS

from memory import (
    WorkingMemory,
    EpisodicStore,
    SemanticStore,
    route_memory,
    build_context_string,
)
from ai import get_ai_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

_start_time = time.time()

working_mem = WorkingMemory(max_size=500)
episodic_mem = EpisodicStore(db_path="memory_bus.db")
semantic_mem = SemanticStore(persist_path="./chroma_db")


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "uptime_seconds": int(time.time() - _start_time)})


@app.route("/memory/write", methods=["POST"])
def memory_write():
    data = request.get_json() or {}
    mem_type = data.get("type", "episodic")
    content = data.get("content", "")
    source = data.get("source", "unknown")
    confidence = float(data.get("confidence", 1.0))
    tags = data.get("tags", [])

    if mem_type == "working":
        key = data.get("key")
        if not key:
            return jsonify({"error": "key required for working memory"}), 400
        ttl = float(data.get("ttl", 3600))
        working_mem.set(key, content, ttl)
        return jsonify({"status": "ok", "id": key, "type": mem_type})

    if mem_type == "episodic":
        memory_id = episodic_mem.write(content, source, confidence, tags)
    elif mem_type == "semantic":
        memory_id = semantic_mem.write(content, source, confidence, tags)
    else:
        return jsonify({"error": f"Unknown type: {mem_type}"}), 400

    return jsonify({"status": "ok", "id": memory_id, "type": mem_type})


@app.route("/memory/recall", methods=["GET"])
def memory_recall():
    mem_type = request.args.get("type", "working")
    q = request.args.get("q", "")
    since = request.args.get("since")
    until = request.args.get("until")
    top_k = int(request.args.get("top_k", 5))

    if mem_type == "working":
        return jsonify({"results": working_mem.all_keys()})

    if mem_type == "episodic":
        if not since or not until:
            return jsonify({"error": "since and until required for episodic recall"}), 400
        results = episodic_mem.recall_by_range(since, until)
        return jsonify({"results": results})

    if mem_type == "semantic":
        results = semantic_mem.search(q, top_k)
        return jsonify({"results": results})

    return jsonify({"error": f"Unknown type: {mem_type}"}), 400


@app.route("/memory/context", methods=["GET"])
def memory_context():
    return jsonify(working_mem.all_keys())


@app.route("/memory/<memory_id>", methods=["DELETE"])
def memory_delete(memory_id):
    if working_mem.delete(memory_id):
        return jsonify({"status": "ok", "deleted_from": "working"})
    if episodic_mem.forget(memory_id):
        return jsonify({"status": "ok", "deleted_from": "episodic"})
    if semantic_mem.forget(memory_id):
        return jsonify({"status": "ok", "deleted_from": "semantic"})
    return jsonify({"error": "Memory not found"}), 404


@app.route("/memory/flush", methods=["POST"])
def memory_flush():
    working_mem.flush()
    return jsonify({"status": "ok", "message": "Working memory cleared"})


@app.route("/info", methods=["GET"])
def info():
    keys = working_mem.all_keys()
    return jsonify({
        "working_memory_keys": len(keys),
        "uptime_seconds": int(time.time() - _start_time),
    })


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    message = data.get("message", "")
    ai_choice = data.get("ai", "ollama")
    api_key = data.get("api_key") or ""
    model = data.get("model", "llama3")

    # STEP 1 — MEMORY ROUTING
    routed_types = route_memory(message)

    # STEP 2 — FETCH MEMORIES
    fetched = {"working": {}, "episodic": [], "semantic": []}

    fetched["working"] = working_mem.all_keys()

    if "episodic" in routed_types:
        since = (datetime.utcnow() - timedelta(days=7)).isoformat()
        until = datetime.utcnow().isoformat()
        episodic_results = episodic_mem.recall_by_range(since, until)
        fetched["episodic"] = episodic_results[-5:]

    if "semantic" in routed_types:
        semantic_results = semantic_mem.search(message, top_k=5)
        filtered = [
            r for r in semantic_results
            if r.get("confidence", 0) >= 0.70 and r.get("similarity", 0) >= 0.75
        ]
        fetched["semantic"] = filtered[:3]

    # STEP 3 — SAFETY NET
    if "semantic" not in routed_types:
        safety_results = semantic_mem.search(message, top_k=3)
        high_relevance = [r for r in safety_results if r.get("similarity", 0) >= 0.80]
        existing_ids = {r["id"] for r in fetched["semantic"]}
        for r in high_relevance[:2]:
            if r["id"] not in existing_ids:
                fetched["semantic"].append(r)
                existing_ids.add(r["id"])

    # STEP 4 — BUILD CONTEXT STRING
    context_string, memories_used, memory_breakdown = build_context_string(fetched)

    # STEP 5 — CALL AI
    ai_response, error = get_ai_response(message, context_string, ai_choice, api_key, model)
    if error:
        return jsonify({"error": error}), 400

    # STEP 6 — SAVE TO EPISODIC
    episodic_mem.write(
        f"User asked ({ai_choice}): {message[:200]}",
        source=ai_choice,
        confidence=1.0,
        tags=["chat"],
    )

    # STEP 7 — RETURN
    return jsonify({
        "response": ai_response,
        "ai_used": ai_choice,
        "context_injected": context_string,
        "memories_used": memories_used,
        "memory_breakdown": memory_breakdown,
    })


if __name__ == "__main__":
    logger.info("AI Memory Bus backend starting on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
