# juce-rag-server — folder tree

```
juce-rag-server/
├── .env.example
├── .vscode/
│   └── settings.json
├── agent.py
├── mcp_juce_bridge.py
├── rag_client.py
├── server.py
└── stress_test.py
```

## Notes

- **Excluded from tree:** `venv/`, `.env` (local secrets).
- **Entry point:** `server.py` — MCP server.
- **RAG:** `rag_client.py`, `agent.py` — RAG client and agent logic.
- **Bridge:** `mcp_juce_bridge.py` — JUCE ↔ MCP integration.
