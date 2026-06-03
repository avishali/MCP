#!/usr/bin/env python3

import json
from pathlib import Path

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


@mcp.tool()
def find_project_file(project: str, role: str = "") -> str:
    """
    Locate project files by project name and optional role.
    """
    entries = _load_project_index()
    project_query = _normalise(project)
    role_query = _normalise(role)

    matches = []
    for entry in entries:
        project_name = str(entry.get("project_name", ""))
        file_role = str(entry.get("file_role", ""))
        file_path = str(entry.get("file_path", ""))

        project_matches = (
            not project_query
            or project_query in _normalise(project_name)
            or project_query in _normalise(file_path)
        )
        role_matches = (
            not role_query
            or role_query == _normalise(file_role)
            or role_query in _normalise(file_path)
        )

        if project_matches and role_matches:
            matches.append(entry)

    return _format_project_matches(matches, project, role)


@mcp.tool()
def search_project_files(query: str, project: str = "") -> str:
    """
    Search indexed project paths for a filename or path fragment.
    """
    entries = _load_project_index()
    query_text = _normalise(query)
    project_query = _normalise(project)

    matches = []
    for entry in entries:
        project_name = str(entry.get("project_name", ""))
        file_path = str(entry.get("file_path", ""))
        haystack = _normalise(f"{project_name} {file_path}")

        if query_text in haystack and (not project_query or project_query in haystack):
            matches.append(entry)

    return _format_project_matches(matches, project or query, "search")


def _load_project_index() -> list[dict]:
    index_path = Path(__file__).with_name("project_structure.json")
    if not index_path.exists():
        return []

    return json.loads(index_path.read_text(encoding="utf-8"))


def _normalise(text: str) -> str:
    return (text or "").strip().casefold()


def _format_project_matches(matches: list[dict], project: str, role: str) -> str:
    if not matches:
        return (
            f"No indexed project files matched project={project!r}, role={role!r}. "
            "Run melech_internal_server/ingest_projects.py to refresh the index."
        )

    lines = [f"Matched {len(matches)} file(s). Showing first 40:"]
    for entry in matches[:40]:
        lines.append(
            f"- {entry.get('project_name')} | {entry.get('file_role')} | "
            f"{entry.get('file_path')}"
        )

    return "\n".join(lines)


# ===============================
# Entry Point
# ===============================

if __name__ == "__main__":
    mcp.run()