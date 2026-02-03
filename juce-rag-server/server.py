#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Optional: only needed if you actually configure Chroma.
# pip install chromadb
try:
    import chromadb  # type: ignore
except Exception:
    chromadb = None  # type: ignore


load_dotenv()

APP_HOST = os.getenv("JUCE_RAG_HTTP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("JUCE_RAG_HTTP_PORT", "8000"))

CHROMA_HOST = os.getenv("CHROMA_HOST", "").strip()
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "").strip()
CHROMA_TENANT = os.getenv("CHROMA_TENANT", "").strip()
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "").strip()
JUCE_RAG_COLLECTION = os.getenv("JUCE_RAG_COLLECTION", "juce_docs").strip()

# If you want a local fallback later, define JUCE_RAG_LOCAL_DIR and implement ingestion.
JUCE_RAG_LOCAL_DIR = os.getenv("JUCE_RAG_LOCAL_DIR", "").strip()

app = FastAPI(title="JUCE RAG Server", version="1.0")


class SearchRequest(BaseModel):
    query: str
    k: int = 5


def _chroma_client():
    if chromadb is None:
        raise RuntimeError("chromadb is not installed. Run: pip install chromadb")

    if not CHROMA_HOST:
        return None

    # This is intentionally conservative: if you’re using Chroma Cloud, you’ll
    # likely use an HttpClient with auth headers. Keep it simple for now.
    # Adjust based on your actual Chroma deployment.
    #
    # For many hosted setups, something like:
    # chromadb.HttpClient(host=..., port=..., ssl=True, headers={...})
    #
    # Here we treat CHROMA_HOST as host:port or host only.
    return chromadb.HttpClient(host=CHROMA_HOST)


@app.post("/search")
def search(req: SearchRequest) -> Dict[str, Any]:
    q = (req.query or "").strip()
    k = max(1, min(int(req.k or 5), 20))

    if not q:
        raise HTTPException(status_code=400, detail="query is required")

    # 1) Try Chroma if configured
    if CHROMA_HOST:
        try:
            client = _chroma_client()
            if client is None:
                raise RuntimeError("CHROMA_HOST set but client is None")

            col = client.get_or_create_collection(JUCE_RAG_COLLECTION)
            res = col.query(query_texts=[q], n_results=k)

            # Normalize results to {source, content}
            out: List[Dict[str, str]] = []
            docs = (res.get("documents") or [[]])[0]
            metas = (res.get("metadatas") or [[]])[0]

            for i, doc in enumerate(docs):
                meta = metas[i] if i < len(metas) else {}
                source = "Unknown"
                if isinstance(meta, dict):
                    source = str(meta.get("source", meta.get("path", "Unknown")))
                out.append({"source": source, "content": str(doc)})

            return {"results": out}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chroma query failed: {e}")

    # 2) No Chroma configured -> fail loudly (so you immediately know why it’s empty)
    raise HTTPException(
        status_code=500,
        detail=(
            "RAG backend not configured. Set CHROMA_HOST (+ credentials) "
            "or implement local mode via JUCE_RAG_LOCAL_DIR."
        ),
    )

if __name__ == "__main__":
    uvicorn.run("server:app", host=APP_HOST, port=APP_PORT, reload=False)