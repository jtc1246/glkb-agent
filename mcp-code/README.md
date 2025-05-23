# MCP Client and Servers

This repository uses both server and client code from the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) project.

It provides a setup for running a simple Claude LLM with MCP tools. The model will call a tool **at most once per query**.

---

## Getting Started

### 1. Set Up the Virtual Environment

Navigate to the `mcp-client` directory and create a virtual environment:

```bash
uv venv
source .venv/bin/activate
uv add mcp anthropic wikipedia arxiv pymed duckduckgo_search python-dotenv
```

### 2. Configure API Access
Create a .env file inside the mcp-client directory and add your Anthropic API key:
```
ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_API_KEY>
```
Replace ```<YOUR_ANTHROPIC_API_KEY>``` with your actual API key.

### 3. Run the Client
To test the LLM on one of the available servers, run:
```bash
python test.py <server_name>
```

Where ```<server_name>``` can be any of the following:

```search```

```arxiv```

```wikipedia```

```pubmed```

The script uses ```pubmedqa.json``` as the default test suite. After execution, performance statistics will be printed to the console.