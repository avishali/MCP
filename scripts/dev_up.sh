#!/bin/bash
set -euo pipefail

ROOT="/Users/avishaylidani/DEV/GitHubRepo/MelechDSP/melechdsp-hq/MCP"
PY="$ROOT/.venv/bin/python"
HOST="127.0.0.1"
PORT=8000

RAG_PID=""

cleanup() {
  if [[ -n "${RAG_PID}" ]] && kill -0 "${RAG_PID}" 2>/dev/null; then
    echo "Stopping JUCE RAG backend (pid=${RAG_PID})..."
    kill "${RAG_PID}" 2>/dev/null || true
    sleep 0.5
    if kill -0 "${RAG_PID}" 2>/dev/null; then
      kill -9 "${RAG_PID}" 2>/dev/null || true
    fi
  fi
}
trap cleanup EXIT INT TERM

echo "Checking port ${PORT}..."
EXISTING_PID="$(lsof -ti :${PORT} 2>/dev/null || true)"

if [[ -n "${EXISTING_PID}" ]]; then
  EXISTING_ARGS="$(ps -p "${EXISTING_PID}" -o args= 2>/dev/null || true)"
  echo "Port ${PORT} is in use by PID ${EXISTING_PID}: ${EXISTING_ARGS}"

  # Only auto-kill if it looks like our Python/uvicorn dev server
  if echo "${EXISTING_ARGS}" | grep -Eqi 'python|uvicorn|server\.py|fastapi'; then
    echo "Killing existing dev server on port ${PORT} (pid=${EXISTING_PID})..."
    kill "${EXISTING_PID}" 2>/dev/null || true
    sleep 0.5
    if lsof -ti :${PORT} >/dev/null 2>&1; then
      kill -9 "${EXISTING_PID}" 2>/dev/null || true
    fi
  else
    echo "Refusing to kill PID ${EXISTING_PID} automatically (doesn't look like python/uvicorn)."
    echo "Kill it manually if it's safe: kill ${EXISTING_PID}"
    exit 1
  fi
fi

echo "Starting JUCE RAG backend..."
cd "${ROOT}/juce-rag-server"

export JUCE_RAG_HTTP_HOST="${HOST}"
export JUCE_RAG_HTTP_PORT="${PORT}"

"${PY}" server.py &
RAG_PID=$!

# Quick bind check (fail fast if it didn’t actually bind)
sleep 0.5
if ! lsof -i :${PORT} >/dev/null 2>&1; then
  echo "ERROR: server.py did not bind to ${HOST}:${PORT}."
  echo "PID=${RAG_PID}"
  exit 1
fi

echo "MelechDSP MCP stack online"
echo "Open Cursor to connect MCP tools"

wait "${RAG_PID}"
