# MCP Repository Structure

```
MCP/
├── .cursorrules
├── .env.example
├── .gitignore
├── claude_desktop_config.example.json
├── DELIVERABLE.txt
├── MCP.code-workspace
├── README.md
│
├── config/
│   └── local_paths.example.json
│
├── dsp_algorithms_server/
│   ├── ingest.py
│   ├── schema.json
│   └── server.py
│
├── juce_api_server/
│   ├── ingest_juce.py
│   ├── schema.json
│   └── server.py
│
├── juce-rag-server/
│   ├── .vscode/
│   │   └── settings.json
│   ├── agent.py
│   ├── mcp_juce_bridge.py
│   ├── rag_client.py
│   ├── server.py
│   └── stress_test.py
│
├── melech_internal_server/
│   ├── ingest_projects.py
│   ├── schema.json
│   └── server.py
│
└── tools/
    └── mcp/
        └── common/
            └──  mcp_server_base.py
```

## Mermaid diagram

```mermaid
flowchart TB
    subgraph root["MCP (root)"]
        A[.cursorrules]
        B[.env.example]
        C[.gitignore]
        D[claude_desktop_config.example.json]
        E[DELIVERABLE.txt]
        F[MCP.code-workspace]
        G[README.md]
    end

    subgraph config["config/"]
        H[local_paths.example.json]
    end

    subgraph dsp["dsp_algorithms_server/"]
        I[ingest.py]
        J[schema.json]
        K[server.py]
    end

    subgraph juce_api["juce_api_server/"]
        L[ingest_juce.py]
        M[schema.json]
        N[server.py]
    end

    subgraph juce_rag["juce-rag-server/"]
        O[.vscode/settings.json]
        P[agent.py]
        Q[mcp_juce_bridge.py]
        R[rag_client.py]
        S[server.py]
        T[stress_test.py]
    end

    subgraph melech["melech_internal_server/"]
        U[ingest_projects.py]
        V[schema.json]
        W[server.py]
    end

    subgraph tools["tools/mcp/common/"]
        X[" mcp_server_base.py"]
    end

    root --> config
    root --> dsp
    root --> juce_api
    root --> juce_rag
    root --> melech
    root --> tools
```
