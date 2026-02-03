#!/bin/bash
set -e

ROOT="/Users/avishaylidani/DEV/GitHubRepo/MCP"
PY="$ROOT/.venv/bin/python"

echo "Starting JUCE RAG backend..."
cd "$ROOT/juce-rag-server"
$PY server.py &

sleep 2

echo "MelechDSP MCP stack online"
echo "Open Cursor to connect MCP tools"

wait