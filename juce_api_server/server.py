#!/usr/bin/env python3

import os
from mcp.server.fastmcp import FastMCP

# ===============================
# MCP Setup
# ===============================

SERVER_NAME = "JUCE API Docs"

mcp = FastMCP(SERVER_NAME)


# ===============================
# Tools
# ===============================

@mcp.tool()
def health() -> str:
    """
    Health check for MCP clients (Cursor / Claude).
    """
    return f"{SERVER_NAME} OK"


@mcp.tool()
def juce_class(name: str) -> str:
    """
    Simple JUCE API lookup stub.
    Replace this with your real JUCE index / RAG logic.
    """
    name = (name or "").strip()
    if not name:
        return "Please provide a JUCE class name."

    return (
        f"JUCE class '{name}'\n\n"
        "This server is running correctly.\n"
        "Hook this tool to your JUCE docs index or RAG backend next."
    )


# ===============================
# Entry Point
# ===============================

if __name__ == "__main__":
    print("JUCE API MCP server running (stdio). Waiting for client...", flush=True)
    mcp.run()