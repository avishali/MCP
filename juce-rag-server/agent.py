import os
import requests
from dotenv import load_dotenv

load_dotenv()

RAG_SEARCH_URL = os.environ.get("JUCE_RAG_SEARCH_URL", "http://localhost:8000/search")


def retrieve_docs(query: str, k: int = 5):
    """Asks your local RAG server for context. Returns list of results."""
    query = (query or "").strip()
    if not query:
        return []

    try:
        resp = requests.post(RAG_SEARCH_URL, json={"query": query, "k": k}, timeout=30)
        if resp.status_code == 200:
            payload = resp.json()
            # Expected: {"results":[{"content": "...", "source": "...", ...}, ...]}
            results = payload.get("results", [])
            if isinstance(results, list):
                return results
    except Exception as e:
        print(f"RAG Connection Error: {e}")

    return []


def query_juce_rag(query: str, top_k: int = 3):
    """
    MCP bridge entry point.
    Returns (answer_text, sources_dict).
    No OpenAI key required.
    """
    results = retrieve_docs(query, k=top_k)
    if not results:
        return ("No results from JUCE RAG store.", {"rag_url": RAG_SEARCH_URL})

    # Build a compact, grounded response: top_k snippets
    chunks = []
    sources = {"rag_url": RAG_SEARCH_URL, "hits": []}

    for r in results[: max(1, int(top_k))]:
        content = (r.get("content") or "").strip()
        src = r.get("source") or r.get("file") or r.get("path") or "unknown"

        if content:
            chunks.append(f"Source: {src}\n{content[:900]}")
            sources["hits"].append(src)

    answer = "\n\n---\n\n".join(chunks) if chunks else "No usable content in results."
    return (answer, sources)


def _get_openai_client():
    """
    Lazy OpenAI init: only needed if you call generate_code().
    Keeps MCP retrieval working without OPENAI_API_KEY.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and set OPENAI_API_KEY."
        )

    # Import only when needed
    from openai import OpenAI  # type: ignore

    return OpenAI(api_key=api_key)


def generate_code(user_query: str):
    """
    Optional: LLM codegen using retrieved context.
    Requires OPENAI_API_KEY.
    """
    client = _get_openai_client()

    print(f"🔍 Searching docs for: '{user_query}'...")
    results = retrieve_docs(user_query, k=5)

    context_text = "\n\n".join(
        [f"--- DOCUMENTATION SEGMENT ---\n{(r.get('content') or '')}" for r in results]
    )

    if not context_text:
        print("⚠️ Warning: No documentation found. LLM might hallucinate.")

    system_prompt = f"""
You are an expert C++ Audio Developer specializing in the JUCE framework.
Your goal is to write production-ready, real-time safe C++ code using the provided context.

### CRITICAL INSTRUCTION: STRICT CONTEXT ADHERENCE
You must ONLY use classes, functions, and method signatures found in the "DOCUMENTATION CONTEXT" provided below.
- If a function is not in the context, DO NOT assume it exists.
- DO NOT use deprecated classes (e.g., ScopedPointer, AudioProcessorGraph::Node).
- If the context is insufficient to answer the request, state exactly what is missing rather than inventing code.

### DOCUMENTATION CONTEXT (Immutable Truth):
{context_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    prompt = "Explain how AudioProcessorValueTreeState attachments work."
    answer, sources = query_juce_rag(prompt, top_k=3)
    print(answer)
    print("\nSOURCES:", sources)