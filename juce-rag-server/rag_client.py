"""
Lightweight client for the local JUCE RAG server.
Use from scripts, agents, or Cursor workflows to inject docs into LLM prompts.
"""
import requests


def get_juce_context(query: str, max_results: int = 5) -> str:
    """
    Queries your local RAG server for JUCE documentation.
    Returns a formatted string ready for an LLM system prompt.
    """
    try:
        response = requests.post(
            "http://localhost:8000/search",
            json={"query": query, "k": max_results},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        # Format the results into a clear block for the Agent
        context_parts = []
        for item in data.get("results", []):
            source = item.get("source", "Unknown Source")
            content = item.get("content", "").strip()
            context_parts.append(f"--- SOURCE: {source} ---\n{content}\n")

        return "\n".join(context_parts)

    except Exception as e:
        print(f"RAG Error: {e}")
        return ""


# --- Example Usage ---
# user_prompt = "Write a C++ class that inherits from AudioProcessor"
# docs = get_juce_context(user_prompt)
# print(f"Agent System Prompt:\nUse these docs:\n{docs}...")
