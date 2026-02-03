MelechDSP MCP Environment Setup

1) Create venv (one time)
   cd MCP
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -U pip
   python -m pip install -r requirements.txt

2) Run MCP servers (stdio)
   MCP/.venv/bin/python <server_path>/server.py

3) Run JUCE RAG HTTP backend (port 8000)
   cd MCP/juce-rag-server
   ../.venv/bin/python server.py

4) Do NOT commit secrets
   Use MCP/.env (ignored) and MCP/.env.example
