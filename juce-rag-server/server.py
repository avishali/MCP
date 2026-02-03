import os
import chromadb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# 1. Load the Cloud credentials from .env
load_dotenv()

app = FastAPI(title="JUCE Cloud RAG Server")

# --- CONFIGURATION ---
COLLECTION_NAME = "docs_juce_com"


# ⚠️ THE FIX IS HERE:
# Qwen3-Embedding-0.6B has a default dimension of 1024.
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"

print(f"⏳ Loading Embedding Model: {MODEL_NAME}...")
embedding_function = HuggingFaceEmbeddings(
    model_name=MODEL_NAME,
    model_kwargs={'device': 'cpu',
                  'trust_remote_code': True  }, # Use 'cuda' if you have a GPU
    encode_kwargs={'normalize_embeddings': True}
    
)
print("✅ Model Loaded.")

# 2. Connect to Chroma Cloud
# We use HttpClient for remote/cloud instances
try:
    client = chromadb.HttpClient(
        host=os.getenv("CHROMA_HOST"),
        port=443,
        ssl=True,
        headers={
            "x-chroma-token": os.getenv("CHROMA_API_KEY")
        },
        tenant=os.getenv("CHROMA_TENANT"),
        database=os.getenv("CHROMA_DATABASE")
    )
    print(f"✅ Connected to Chroma Cloud (DB: {os.getenv('CHROMA_DATABASE')})")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    raise

class QueryRequest(BaseModel):
    query: str
    k: int = 5

@app.post("/search")
async def search_docs(request: QueryRequest):
    try:
        collection = client.get_collection(name=COLLECTION_NAME)

        # Embed query using the local HuggingFace model
        query_vector = embedding_function.embed_query(request.query)

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=request.k,
            include=["documents", "metadatas"]
        )

        formatted_results = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "source": results['metadatas'][0][i].get("source", "unknown")
                })

        return {"results": formatted_results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)