from mcp.server.fastmcp import FastMCP
import json
import os

# 1. Initialize Server
mcp = FastMCP("JUCE API Docs")

# 2. Load the Index
DB_PATH = os.path.join(os.path.dirname(__file__), "juce_docs.json")

def load_db():
    try:
        with open(DB_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

juce_data = load_db()

# 3. Define the Search Tool
@mcp.tool()
def search_juce_docs(class_name: str) -> str:
    """
    Search the official JUCE API for class definitions, inheritance, and methods.
    Use this to verify function signatures (e.g., 'Does AudioProcessor have a processBlock?').
    """
    results = []
    query = class_name.lower().replace("juce::", "")
    
    for entry in juce_data:
        # Match class name exactly or partially
        if query in entry['class_name'].lower():
            results.append(
                f"Class: {entry['class_name']}\n"
                f"Module: {entry['module']}\n"
                f"Inherits: {entry['inheritance']}\n"
                f"Snippet:\n{entry['api_signature'][:800]}..." # 800 chars gives enough context
            )
            
    if not results:
        return "No matching JUCE class found."
        
    return "\n---\n".join(results[:2]) # Return top 2 matches to save tokens

if __name__ == "__main__":
    mcp.run()