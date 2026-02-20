[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io/)

# MCP Kubernetes Documentation Server

An MCP (Model Context Protocol) server that provides search and retrieval tools for [Kubernetes](https://kubernetes.io) documentation. This server enables AI assistants like Claude to search and read Kubernetes documentation directly, including markdown pages and structured YAML data files (release schedules, end-of-life information, announcements).

## Features

- **Full-text search** using SQLite FTS5 with BM25 ranking and Porter stemming
- **Section filtering** to narrow search results by documentation category
- **YAML data indexing** for release schedules, EOL releases, and announcements
- **Sparse checkout** for efficient cloning of only the required directories from kubernetes/website
- **Docker support** for portable deployment across projects
- **STDIO transport** for seamless MCP client integration

## Quick Start

### Using the Container Image (Recommended)

The `martoc/mcp-kubernetes-documentation` container image is published to Docker Hub with the documentation index pre-built. Available for `linux/amd64` and `linux/arm64`.

```bash
# Pull and run the server
docker run -i --rm martoc/mcp-kubernetes-documentation:latest
```

### Building Locally with Docker

```bash
# Build the Docker image (includes pre-indexed documentation)
make docker-build

# Test the server
make docker-run
```

### Using uv (Local Development)

```bash
# Initialise the environment
make init

# Build the documentation index
make index

# Run the server
make run
```

## Container Image

The `martoc/mcp-kubernetes-documentation` container image is published to [Docker Hub](https://hub.docker.com/r/martoc/mcp-kubernetes-documentation). It includes the pre-built documentation index so the server is ready to use immediately.

| Property | Value |
|----------|-------|
| Registry | Docker Hub |
| Image | `martoc/mcp-kubernetes-documentation` |
| Platforms | `linux/amd64`, `linux/arm64` |
| Base image | `python:3.12-slim` |
| Index | Pre-built at image build time from `kubernetes/website` `main` branch |

```bash
# Pull the latest image
docker pull martoc/mcp-kubernetes-documentation:latest

# Run the MCP server
docker run -i --rm martoc/mcp-kubernetes-documentation:latest
```

## Configuration

### Claude Code / Claude Desktop

Add to your `.mcp.json` or global settings to use the published container image:

```json
{
  "mcpServers": {
    "kubernetes-documentation": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "martoc/mcp-kubernetes-documentation:latest"]
    }
  }
}
```

For a locally built Docker image:

```json
{
  "mcpServers": {
    "kubernetes-documentation": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp-kubernetes-documentation"]
    }
  }
}
```

For local development without Docker:

```json
{
  "mcpServers": {
    "kubernetes-documentation": {
      "command": "uv",
      "args": ["run", "mcp-kubernetes-documentation"],
      "cwd": "/path/to/mcp-kubernetes-documentation"
    }
  }
}
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_documentation` | Search Kubernetes documentation by keyword query with optional section filtering |
| `read_documentation` | Retrieve the full content of a specific documentation page |

### search_documentation

Search Kubernetes documentation using full-text search with stemming support.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search terms (supports stemming) |
| `section` | string | No | None | Filter by section (e.g., docs, blog, releases) |
| `limit` | integer | No | 10 | Maximum results (1-50) |

**Common Sections:** `docs`, `blog`, `releases`, `announcements`, `case-studies`, `community`

### read_documentation

Retrieve the full content of a documentation page.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Relative path to document (from search results) |

## CLI Commands

```bash
# Build/rebuild the documentation index
uv run kubernetes-docs-index index
uv run kubernetes-docs-index index --rebuild
uv run kubernetes-docs-index index --branch main

# Show index statistics
uv run kubernetes-docs-index stats
```

## Development

```bash
make init       # Initialise development environment
make build      # Run full build (lint, typecheck, test)
make test       # Run tests with coverage
make format     # Format code
make lint       # Run linter
make typecheck  # Run type checker
```

## Documentation

- [USAGE.md](USAGE.md) - Detailed usage instructions
- [CODESTYLE.md](CODESTYLE.md) - Code style guidelines
- [CLAUDE.md](CLAUDE.md) - Claude Code instructions

## Licence

This project is licensed under the MIT Licence - see the [LICENSE](LICENSE) file for details.
