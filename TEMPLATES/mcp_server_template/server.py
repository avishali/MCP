#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP

SERVER_NAME = "MelechDSP MCP Server"

mcp = FastMCP(SERVER_NAME)

@mcp.tool()
def health() -> str:
    return f"{SERVER_NAME} OK"

@mcp.tool()
def version() -> str:
    return "melechdsp-mcp v1.0"

if __name__ == "__main__":
    print(f"{SERVER_NAME} running (stdio). Waiting for client...", flush=True)
    mcp.run()