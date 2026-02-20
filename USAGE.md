# Usage Guide

This guide provides detailed instructions for using the MCP Kubernetes Documentation Server.

## Installation

### Prerequisites

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- Docker (optional, for containerised deployment)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/martoc/mcp-kubernetes-documentation.git
   cd mcp-kubernetes-documentation
   ```

2. Initialise the development environment:
   ```bash
   make init
   ```

3. Build the documentation index:
   ```bash
   make index
   ```

## Indexing Documentation

### Initial Indexing

Index the Kubernetes documentation from the main branch:

```bash
uv run kubernetes-docs-index index
```

### Rebuilding the Index

Clear the existing index and rebuild from scratch:

```bash
uv run kubernetes-docs-index index --rebuild
```

### Indexing a Specific Branch

Index documentation from a specific Git branch:

```bash
uv run kubernetes-docs-index index --branch release-1.35
```

### Index Statistics

View the number of indexed documents:

```bash
uv run kubernetes-docs-index stats
```

## Running the MCP Server

### Using the Container Image (Recommended)

The `martoc/mcp-kubernetes-documentation` container image is published to Docker Hub with the documentation index pre-built. Available for `linux/amd64` and `linux/arm64`.

```bash
# Pull and run the server
docker run -i --rm martoc/mcp-kubernetes-documentation:latest
```

### Local Development

Run the server directly using uv:

```bash
make run
# or
uv run mcp-kubernetes-documentation
```

### Building a Local Docker Image

Build and run the server in a Docker container:

```bash
make docker-build
make docker-run
```

## MCP Client Configuration

### Claude Code (Container Image)

Add to your project's `.mcp.json` to use the published container image:

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

### Claude Code (Local Development)

Add to your project's `.mcp.json` for local development:

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

### Claude Desktop

Add to your Claude Desktop configuration:

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

## Using the Tools

### Searching Documentation

Search for topics in Kubernetes documentation:

```
Search for "pod lifecycle"
Search for "deployment strategy" in section "docs"
Search for "release schedule" with limit 20
```

Example response:
```json
{
  "query": "pod lifecycle",
  "section_filter": null,
  "result_count": 5,
  "results": [
    {
      "title": "Pod Lifecycle",
      "url": "https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/",
      "path": "docs/concepts/workloads/pods/pod-lifecycle.md",
      "section": "docs",
      "snippet": "...pod lifecycle phases include Pending, Running...",
      "relevance_score": 12.5432
    }
  ]
}
```

### Reading Documentation

Retrieve the full content of a specific page:

```
Read documentation at path "docs/concepts/workloads/pods/pod-lifecycle.md"
```

Example response:
```json
{
  "path": "docs/concepts/workloads/pods/pod-lifecycle.md",
  "title": "Pod Lifecycle",
  "description": "Describes the lifecycle of a Pod",
  "section": "docs",
  "url": "https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/",
  "content": "# Pod Lifecycle\n\n..."
}
```

## Common Sections

The Kubernetes documentation is organised into several sections:

- **docs**: Main documentation (concepts, tasks, tutorials, references)
- **blog**: Blog posts and announcements
- **releases**: Release schedules and end-of-life information
- **announcements**: Scheduled website announcements
- **case-studies**: Case studies from Kubernetes users
- **community**: Community information and contribution guides

Use these section names with the `section` parameter to filter search results.

## Development Workflow

### Code Quality Checks

Run all code quality checks:

```bash
make build
```

This runs:
- Linter (ruff)
- Type checker (mypy)
- Tests with coverage (pytest)

### Individual Checks

```bash
make lint       # Run linter only
make typecheck  # Run type checker only
make test       # Run tests only
make format     # Format code
```

### Updating Dependencies

Update the lock file:

```bash
make generate
```

## Troubleshooting

### Index Build Fails

If the index build fails, try:

1. Check your internet connection
2. Verify Git is installed and accessible
3. Try rebuilding with a different branch:
   ```bash
   uv run kubernetes-docs-index index --rebuild --branch main
   ```

### No Search Results

If searches return no results:

1. Verify the index is built:
   ```bash
   uv run kubernetes-docs-index stats
   ```

2. Rebuild the index if necessary:
   ```bash
   uv run kubernetes-docs-index index --rebuild
   ```

### Database Location

The default database location is `data/kubernetes_docs.db`. To use a custom location:

```bash
uv run kubernetes-docs-index index --database /path/to/custom.db
```

## Performance Considerations

- **Initial indexing**: May take several minutes depending on network speed
- **Sparse checkout**: Only `content/en/`, `data/releases/`, and `data/announcements/` are cloned, reducing download size
- **Search performance**: FTS5 with BM25 ranking provides fast, relevant results
- **Memory usage**: Minimal during operation; database is SQLite-based
