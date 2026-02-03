# MCP (Model Context Protocol) Servers

This repository contains MCP servers that provide AI agents with structured access to MelechDSP's codebase, JUCE documentation, and DSP algorithms. These servers enable AI coding assistants to retrieve accurate, context-aware information without relying on web searches.

## Overview

The MCP folder implements the **Trinity Protocol** for AI-assisted development:
1. **Architectural Check** - Locate files within the MelechDSP monorepo
2. **API Verification** - Verify JUCE class signatures and inheritance
3. **Component Reuse** - Search existing DSP algorithms and implementations

## Server Architecture

### 1. `melech_internal_server/` - Project Structure Locator

**Purpose**: Maps the MelechDSP monorepo structure to help AI agents find specific files.

**Tools**:
- `find_project_file(project, role)` - Locate files by project name and role (e.g., "AnalyzerPro", "Editor")

**Data Source**: 
- Scans `AnalyzerPro` and `melechdsp-hq` repositories
- Generates `project_structure.json` via `ingest_projects.py`

**Usage Example**:
```python
find_project_file("AnalyzerPro", "Editor")  # Returns UI editor file paths
```

**Files**:
- `server.py` - FastMCP server implementation
- `ingest_projects.py` - Scans projects and generates index
- `project_structure.json` - Generated index file
- `schema.json` - Tool schema definitions

---

### 2. `juce_api_server/` - JUCE API Documentation

**Purpose**: Provides local access to JUCE framework class definitions, inheritance hierarchies, and method signatures.

**Tools**:
- `search_juce_docs(class_name)` - Search JUCE classes by name

**Data Source**:
- Scans `~/JUCE/modules` directory
- Extracts class definitions, inheritance, and API signatures
- Generates `juce_docs.json` via `ingest_juce.py`

**Usage Example**:
```python
search_juce_docs("AudioProcessor")  # Returns class definition and inheritance
```

**Files**:
- `server.py` - FastMCP server implementation
- `ingest_juce.py` - Scans JUCE modules and generates index
- `juce_docs.json` - Generated index file (not in repo, generated locally)
- `schema.json` - Tool schema definitions

**Note**: Prevents AI agents from hallucinating deprecated JUCE 5 methods by providing accurate JUCE 8 API information.

---

### 3. `dsp_algorithms_server/` - DSP Algorithm Library

**Purpose**: Indexes and searches local C++ DSP implementations from the `melechdsp-hq` shared library.

**Tools**:
- `get_dsp_algorithm(query)` - Search DSP algorithms by name or functionality

**Data Source**:
- Scans `melechdsp-hq/shared/mdsp_dsp/` for `.h`, `.cpp`, `.hpp` files
- Detects processing domain (FrequencyDomain, TimeDomain, ControlRate)
- Identifies SIMD optimizations
- Generates `dsp_index.json` via `ingest.py`

**Usage Example**:
```python
get_dsp_algorithm("filter")  # Returns matching filter implementations
get_dsp_algorithm("FFT")     # Returns frequency domain algorithms
```

**Files**:
- `server.py` - FastMCP server implementation
- `ingest.py` - Scans DSP codebase and generates index
- `dsp_index.json` - Generated index file
- `schema.json` - Tool schema definitions

**Features**:
- Detects SIMD optimizations (`__m128`, `vDSP`)
- Categorizes by processing domain
- Returns code snippets for context

---

### 4. `juce-rag-server/` - Cloud-Based JUCE RAG

**Purpose**: Provides semantic search over JUCE documentation using ChromaDB cloud and HuggingFace embeddings.

**Architecture**:
- FastAPI server (`server.py`) that queries ChromaDB cloud
- Uses `Qwen/Qwen3-Embedding-0.6B` model for embeddings
- MCP bridge (`mcp_juce_bridge.py`) connects to the FastAPI server

**Tools**:
- `search_juce_docs(query)` - Semantic search over JUCE docs

**Configuration**:
- Requires `.env` file with ChromaDB credentials:
  - `CHROMA_HOST`
  - `CHROMA_API_KEY`
  - `CHROMA_TENANT`
  - `CHROMA_DATABASE`

**Files**:
- `server.py` - FastAPI server with ChromaDB integration
- `mcp_juce_bridge.py` - MCP server bridge to FastAPI
- `rag_client.py` - RAG client utilities
- `agent.py` - Agent integration code
- `stress_test.py` - Load testing utilities
- `.env` - Environment variables (not in repo)

**Usage**:
1. Start the FastAPI server: `python server.py` (runs on port 8000)
2. Use `mcp_juce_bridge.py` as the MCP server entry point

---

## Configuration

### Claude Desktop Configuration

The `claude_desktop_config.json` file configures MCP servers for Claude Desktop:

```json
{
  "mcpServers": {
    "melech_dsp": {
      "command": "python3",
      "args": ["/path/to/dsp_algorithms_server/server.py"]
    },
    "juce_docs": {
      "command": "python3",
      "args": ["/path/to/juce_api_server/server.py"]
    }
  }
}
```

**Location**: Typically placed at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS.

### Cursor Integration

MCP servers are automatically discovered by Cursor when configured. The `.cursorrules` file in this repository provides guidance for AI agents:

- Always check local MCP tools before web searches
- Use `melech_dsp` for filters, EQ, algorithms
- Use `juce_docs` for AudioProcessor, Components, JUCE API

---

## Setup and Usage

### Prerequisites

```bash
pip install mcp fastmcp  # For MCP servers
pip install fastapi uvicorn chromadb langchain-huggingface  # For RAG server
```

### Generating Indexes

Before using the servers, generate the index files:

```bash
# Generate DSP algorithm index
cd dsp_algorithms_server
python ingest.py

# Generate JUCE API index
cd ../juce_api_server
python ingest_juce.py

# Generate project structure index
cd ../melech_internal_server
python ingest_projects.py
```

### Running Servers

**Standalone MCP Servers** (stdio mode):
```bash
python dsp_algorithms_server/server.py
python juce_api_server/server.py
python melech_internal_server/server.py
```

**RAG Server** (HTTP mode):
```bash
cd juce-rag-server
python server.py  # Runs on http://localhost:8000
# Then use mcp_juce_bridge.py as the MCP entry point
```

---

## Development Workflow

### The Trinity Protocol

When implementing features, AI agents should follow this order:

1. **Architectural Check** (`melech_internal_server`)
   - Locate correct file paths
   - Verify project structure
   - Determine if feature belongs in AnalyzerPro or VoxScript

2. **API Verification** (`juce_api_server` or `juce-rag-server`)
   - Check JUCE class inheritance
   - Verify method signatures
   - Ensure compatibility with JUCE 8

3. **Component Reuse** (`dsp_algorithms_server`)
   - Search for existing implementations
   - Avoid rewriting existing filters/algorithms
   - Reuse `SimpleEq`, `FrequencyBandProcessor`, etc.

### Error Handling

If a tool returns "No results", agents should:
- Explicitly state: "I checked the local library but found no existing implementation, so I will write a custom one."
- Proceed with implementation only after verification

---

## File Structure

```
MCP/
├── README.md                      # This file
├── .cursorrules                   # AI agent guidance
├── claude_desktop_config.json     # Claude Desktop MCP config
├── MCP.code-workspace             # VS Code workspace
│
├── dsp_algorithms_server/         # DSP algorithm search
│   ├── server.py
│   ├── ingest.py
│   ├── dsp_index.json
│   └── schema.json
│
├── juce_api_server/               # JUCE API documentation
│   ├── server.py
│   ├── ingest_juce.py
│   ├── juce_docs.json            # Generated (not in repo)
│   └── schema.json
│
├── melech_internal_server/        # Project structure locator
│   ├── server.py
│   ├── ingest_projects.py
│   ├── project_structure.json
│   └── schema.json
│
└── juce-rag-server/              # Cloud-based RAG
    ├── server.py                 # FastAPI server
    ├── mcp_juce_bridge.py        # MCP bridge
    ├── rag_client.py
    ├── agent.py
    ├── stress_test.py
    └── .env                      # ChromaDB config (not in repo)
```

---

## Best Practices

1. **Always regenerate indexes** after significant codebase changes
2. **Keep paths updated** in ingest scripts if repository locations change
3. **Test MCP servers** before deploying to ensure they return accurate results
4. **Use semantic search** (RAG server) for complex queries, keyword search for exact matches
5. **Monitor token usage** - servers limit results to top matches to save tokens

---

## Troubleshooting

### Server Not Found
- Verify Python path in `claude_desktop_config.json`
- Check that `PYTHONUNBUFFERED=1` is set in environment

### Empty Results
- Regenerate index files using ingest scripts
- Verify source paths in ingest scripts match your repository locations
- Check file permissions on index JSON files

### RAG Server Connection Errors
- Ensure FastAPI server is running on port 8000
- Verify `.env` file contains correct ChromaDB credentials
- Check network connectivity to ChromaDB cloud instance

---

## Future Enhancements

- [ ] Add incremental indexing (only scan changed files)
- [ ] Implement caching for frequently accessed queries
- [ ] Add support for cross-references between algorithms
- [ ] Integrate with CI/CD to auto-regenerate indexes
- [ ] Add metrics/analytics for query patterns
