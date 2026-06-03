#!/usr/bin/env python3

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ===============================
# MCP Setup
# ===============================

SERVER_NAME = "DSP Algorithms"

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
def get_dsp_algorithm(query: str) -> str:
    """
    Search indexed MelechDSP DSP implementations by name, path, or content.
    """
    query_text = _normalise(query)
    if not query_text:
        return "Please provide a DSP search query."

    entries = _load_dsp_index()
    scored = []

    for entry in entries:
        name = str(entry.get("algorithm_name", ""))
        path = str(entry.get("source_path", ""))
        snippet = str(entry.get("code_snippet", ""))
        haystack = _normalise(f"{name} {path} {snippet}")

        if query_text not in haystack:
            continue

        score = 0
        if query_text == _normalise(name):
            score += 100
        if query_text in _normalise(name):
            score += 50
        if query_text in _normalise(path):
            score += 25
        scored.append((score, entry))

    scored.sort(key=lambda item: item[0], reverse=True)
    return _format_dsp_matches([entry for _, entry in scored], query)


@mcp.tool()
def list_dsp_algorithms(limit: int = 40) -> str:
    """
    List indexed DSP implementations.
    """
    entries = _load_dsp_index()
    return _format_dsp_matches(entries[: max(0, limit)], "list")


def _load_dsp_index() -> list[dict]:
    index_path = Path(__file__).with_name("dsp_index.json")
    if not index_path.exists():
        return []

    return json.loads(index_path.read_text(encoding="utf-8"))


def _normalise(text: str) -> str:
    return (text or "").strip().casefold()


def _format_dsp_matches(matches: list[dict], query: str) -> str:
    if not matches:
        return (
            f"No indexed DSP implementation matched query={query!r}. "
            "Run dsp_algorithms_server/ingest.py to refresh the index."
        )

    lines = [f"Matched {len(matches)} DSP file(s). Showing first 20:"]
    for entry in matches[:20]:
        lines.extend(
            [
                f"- {entry.get('algorithm_name')} | {entry.get('processing_domain')} | "
                f"{entry.get('source_path', '(path not indexed)')}",
                f"  latency_samples={entry.get('latency_samples')} "
                f"simd_optimized={entry.get('simd_optimized')}",
                "  snippet:",
                _indent_snippet(str(entry.get("code_snippet", ""))),
            ]
        )

    return "\n".join(lines)


def _indent_snippet(snippet: str) -> str:
    trimmed = snippet.strip()
    if len(trimmed) > 1200:
        trimmed = trimmed[:1200].rstrip() + "\n..."

    return "\n".join(f"    {line}" for line in trimmed.splitlines())


# ===============================
# Entry Point
# ===============================

if __name__ == "__main__":
    mcp.run()