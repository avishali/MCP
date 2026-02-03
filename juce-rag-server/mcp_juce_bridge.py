from mcp.server.fastmcp import FastMCP
import requests
import os

mcp = FastMCP("JUCE RAG")

RAG_SERVER_URL = os.getenv(
    "JUCE_RAG_URL",
    "http://127.0.0.1:8000/search"
)


@mcp.tool()
def search_juce_docs(query: str, k: int = 5) -> str:
    """
    Semantic search over JUCE docs via the local HTTP RAG server.
    """
    try:
        resp = requests.post(RAG_SERVER_URL, json={"query": query, "k": k}, timeout=15)
        if resp.status_code != 200:
            return f"RAG server error {resp.status_code}: {resp.text}"

        data = resp.json()
        results = data.get("results", [])
        if not results:
            return "No relevant documentation found."

        out = []
        for item in results:
            source = item.get("source", "Unknown")
            content = (item.get("content", "") or "").strip()
            if content:
                out.append(f"--- SOURCE: {source} ---\n{content}")

        return "\n\n".join(out) if out else "No relevant documentation found."
    except requests.exceptions.ConnectionError:
        return "Error: cannot connect to RAG HTTP server. Start: juce-rag-server/server.py"
    except Exception as e:
        return f"Error searching docs: {e}"


if __name__ == "__main__":
    mcp.run()