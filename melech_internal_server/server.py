#!/usr/bin/env python3

import os
import sys
import json
import argparse
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


# ==========================
# CONFIG / ENV MANAGEMENT
# ==========================

REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY"
]

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 3001


def _fatal(msg: str):
    print(f"[MCP][FATAL] {msg}", file=sys.stderr)
    sys.exit(1)


def load_env():
    """
    Load environment variables from .env if python-dotenv is available.
    This is optional and never required in production or CI.
    """
    if load_dotenv:
        load_dotenv(override=False)


def get_required_env():
    """
    Fetch and validate required environment variables.
    """
    missing = []
    values = {}

    for key in REQUIRED_ENV_VARS:
        val = os.environ.get(key)
        if not val:
            missing.append(key)
        else:
            values[key] = val

    if missing:
        _fatal(
            "Missing required environment variables: "
            + ", ".join(missing)
            + "\nSet them in your shell or .env file before running."
        )

    return values


# ==========================
# PATH MANAGEMENT
# ==========================

def resolve_project_root():
    """
    Resolves the MCP project root safely even when used as a git submodule.
    """
    return Path(__file__).resolve().parent


def load_local_paths_config():
    """
    Optional portable config for multi-repo setups.
    tools/mcp/config/local_paths.json (ignored by git)
    """
    root = resolve_project_root()
    config_path = root / "config" / "local_paths.json"

    if not config_path.exists():
        return {}

    try:
        return json.loads(config_path.read_text())
    except Exception as e:
        _fatal(f"Failed to parse local_paths.json: {e}")


# ==========================
# SERVER LOGIC (STUB HOOK)
# ==========================

def run_server(host: str, port: int, api_key: str, local_paths: dict):
    """
    Replace this stub with your real MCP server logic.
    """
    print("[MCP] Server starting")
    print(f"[MCP] Host: {host}")
    print(f"[MCP] Port: {port}")
    print(f"[MCP] Local paths loaded: {bool(local_paths)}")

    # Example: never print secrets
    print("[MCP] API key loaded: YES")

    # ---- YOUR SERVER LOOP HERE ----
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n[MCP] Server shutting down cleanly")


# ==========================
# CLI
# ==========================

def parse_args():
    parser = argparse.ArgumentParser(description="MCP Server")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    return parser.parse_args()


def main():
    load_env()
    args = parse_args()
    env = get_required_env()
    local_paths = load_local_paths_config()

    run_server(
        host=args.host,
        port=args.port,
        api_key=env["OPENAI_API_KEY"],
        local_paths=local_paths
    )


if __name__ == "__main__":
    main()