#!/usr/bin/env python3

from mcp.server.fastmcp import FastMCP

# ===============================
# MCP Setup
# ===============================

SERVER_NAME = "MelechDSP Server"

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
def version() -> str:
    """
    Returns server version string.
    """
    return "melechdsp-mcp v1.0"


# ===============================
# Entry Point
# ===============================

if __name__ == "__main__":
    print(f"{SERVER_NAME} MCP server running (stdio). Waiting for client...", flush=True)
    mcp.run()