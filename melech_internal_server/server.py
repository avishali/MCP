from mcp.server.fastmcp import FastMCP
import json
import os

mcp = FastMCP("MelechDSP Architecture")
DB_PATH = os.path.join(os.path.dirname(__file__), "project_structure.json")

def load_db():
    try:
        with open(DB_PATH, "r") as f: return json.load(f)
    except: return []

data = load_db()

@mcp.tool()
def find_project_file(project: str, role: str) -> str:
    """
    Locate specific files within the MelechDSP monorepo.
    Usage: find_project_file("AnalyzerPro", "Editor") to find where the UI code lives.
    """
    results = []
    for entry in data:
        if project.lower() in entry['project_name'].lower() and role.lower() in entry['file_role'].lower():
            results.append(f"Found {entry['file_role']} for {entry['project_name']}: {entry['file_path']}")
            
    return "\n".join(results) if results else "File not found."

if __name__ == "__main__":
    mcp.run()