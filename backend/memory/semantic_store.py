import logging
import math
import time
import uuid
from datetime import datetime

import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class SemanticStore:
    def __init__(self, persist_path: str = "./chroma_db"):
        logger.info("Loading sentence-transformers model all-MiniLM-L6-v2 (first load may take 5-10 seconds)...")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded.")
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name="semantic_memory",
            metadata={"hnsw:space": "cosine"},
        )

    def write(self, content: str, source: str = "unknown", confidence: float = 1.0, tags=None) -> str:
        if tags is None:
            tags = []
        memory_id = f"sem_{uuid.uuid4().hex[:8]}"
        embedding = self.embedder.encode(content).tolist()
        written_at = datetime.utcnow().isoformat()
        tags_str = ",".join(tags) if isinstance(tags, list) else str(tags)
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[
                {
                    "source": source,
                    "confidence": confidence,
                    "tags": tags_str,
                    "written_at": written_at,
                    "reinforcements": 1,
                }
            ],
        )
        return memory_id

    def search(self, query: str, top_k: int = 5) -> list:
        if self.collection.count() == 0:
            return []
        query_embedding = self.embedder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        output = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i, mem_id in enumerate(ids):
            distance = distances[i] if i < len(distances) else 1.0
            similarity = 1.0 - distance
            meta = metadatas[i] if i < len(metadatas) else {}
            content = documents[i] if i < len(documents) else ""
            reinforcements = float(meta.get("reinforcements", 1))
            written_at_str = meta.get("written_at", datetime.utcnow().isoformat())
            try:
                written_ts = datetime.fromisoformat(written_at_str.replace("Z", "+00:00")).timestamp()
            except (ValueError, TypeError):
                written_ts = time.time()
            days_elapsed = (time.time() - written_ts) / 86400
            c_max = 1.0 - math.exp(-0.15 * reinforcements)
            tau = 90.0 * math.log(reinforcements + 1 + 1e-9)
            conf_score = c_max * math.exp(-days_elapsed / tau) if tau > 0 else c_max
            output.append(
                {
                    "id": mem_id,
                    "content": content,
                    "similarity": round(similarity, 4),
                    "confidence": round(conf_score, 4),
                    "source": meta.get("source", "unknown"),
                    "written_at": written_at_str,
                }
            )
        return output

    def forget(self, memory_id: str) -> bool:
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False
