from mcp.server.fastmcp import FastMCP
import requests
import sys

# 1. Create the MCP Server
# "JUCE Docs" is the name the AI will see
mcp = FastMCP("JUCE Docs")

# 2. Define the RAG Server URL
RAG_SERVER_URL = "http://localhost:8000/search"

@mcp.tool()
def search_juce_docs(query: str) -> str:
    """
    Search the official JUCE C++ framework documentation. 
    Use this whenever you need to write JUCE code, check class names, 
    verify function signatures, or understand best practices.
    """
    try:
        # Send the query to your running server.py
        response = requests.post(
            RAG_SERVER_URL, 
            json={"query": query, "k": 5},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Format the results for the AI
        results = data.get("results", [])
        if not results:
            return "No relevant documentation found."
            
        formatted_text = ""
        for item in results:
            source = item.get("source", "Unknown")
            content = item.get("content", "").strip()
            formatted_text += f"\n--- SOURCE: {source} ---\n{content}\n"
            
        return formatted_text

    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the local RAG server. Is 'server.py' running on port 8000?"
    except Exception as e:
        return f"Error searching docs: {str(e)}"

if __name__ == "__main__":
    # This runs the MCP server over standard input/output (stdio)
    mcp.run()