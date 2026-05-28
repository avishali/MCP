#!/usr/bin/env python3
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# ===============================
# MCP Setup
# ===============================

SERVER_NAME = "JUCE API Docs"
SERVER_DIR = Path(__file__).resolve().parent
INDEX_FILE = SERVER_DIR / "juce_docs.json"
MAX_LIMIT = 20

mcp = FastMCP(SERVER_NAME)


@lru_cache(maxsize=1)
def _load_docs() -> list[dict[str, Any]]:
    if not INDEX_FILE.exists():
        return []

    with INDEX_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        return []

    return [entry for entry in data if isinstance(entry, dict)]


def _entry_text(entry: dict[str, Any]) -> str:
    return "\n".join(
        str(entry.get(field, ""))
        for field in ("class_name", "module", "inheritance", "api_signature", "file_path")
    ).lower()


def _format_entry(entry: dict[str, Any]) -> str:
    class_name = str(entry.get("class_name", "Unknown"))
    module = str(entry.get("module", "unknown_module"))
    inheritance = str(entry.get("inheritance", "None"))
    file_path = str(entry.get("file_path", "Unknown"))
    signature = str(entry.get("api_signature", "")).strip()

    if len(signature) > 4000:
        signature = signature[:4000].rstrip() + "\n..."

    return (
        f"--- {class_name} ({module}) ---\n"
        f"File: {file_path}\n"
        f"Inheritance: {inheritance}\n\n"
        f"{signature}"
    )


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
def search_juce_docs(class_name: str, module: str = "", limit: int = 5) -> str:
    """
    Search the local JUCE API index for class names, modules, and signatures.
    """
    query = (class_name or "").strip()
    module_filter = (module or "").strip().lower()
    result_limit = max(1, min(int(limit or 5), MAX_LIMIT))

    if not query:
        return "Please provide a JUCE class name or search query."

    docs = _load_docs()
    if not docs:
        return (
            f"No JUCE docs index found at {INDEX_FILE}. "
            f"Run: {SERVER_DIR / 'ingest_juce.py'}"
        )

    query_lower = query.lower()
    scored: list[tuple[int, dict[str, Any]]] = []

    for entry in docs:
        entry_module = str(entry.get("module", "")).lower()
        if module_filter and module_filter not in entry_module:
            continue

        class_full = str(entry.get("class_name", ""))
        class_simple = class_full.rsplit("::", 1)[-1].lower()
        text = _entry_text(entry)

        if query_lower == class_simple or query_lower == class_full.lower():
            score = 0
        elif class_simple.startswith(query_lower):
            score = 1
        elif query_lower in class_simple:
            score = 2
        elif query_lower in text:
            score = 3
        else:
            continue

        scored.append((score, entry))

    if not scored:
        return f"No JUCE documentation found for '{query}'."

    scored.sort(key=lambda item: (item[0], str(item[1].get("class_name", ""))))
    return "\n\n".join(_format_entry(entry) for _, entry in scored[:result_limit])


@mcp.tool()
def juce_class(name: str) -> str:
    """
    Backwards-compatible wrapper for older MCP prompts.
    """
    return search_juce_docs(name)


# ===============================
# Entry Point
# ===============================

if __name__ == "__main__":
    mcp.run()
