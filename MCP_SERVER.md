# Dockerfile AI MCP Server

This document describes how to set up and use the Dockerfile AI Analyzer as an MCP (Model Context Protocol) server.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that enables AI applications to connect with external data sources and tools. By running Dockerfile AI as an MCP server, you can integrate it with MCP-compatible clients like Claude Desktop, allowing you to analyze Dockerfiles directly from your AI assistant.

## Features

The Dockerfile AI MCP server provides:

### Tools
- **analyze_dockerfile**: Analyze a Dockerfile and get AI-powered recommendations
- **list_analyses**: List all saved analyses and corrected Dockerfiles
- **get_analysis**: Retrieve a specific saved analysis or corrected Dockerfile

### Resources
- Access to saved Dockerfile analyses (as markdown files)
- Access to corrected Dockerfiles

### Prompts
- **analyze-dockerfile**: Pre-built prompt for analyzing a Dockerfile
- **review-dockerfile-changes**: Compare original and corrected Dockerfiles

## Installation

1. Install the package with MCP support:
```bash
pip install -e .
```

2. Verify the MCP server is installed:
```bash
dockerfile-ai-mcp --help
```

## Configuration for Claude Desktop

To use the Dockerfile AI MCP server with Claude Desktop, add it to your Claude Desktop configuration file:

### macOS
Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
Edit: `%APPDATA%\Claude\claude_desktop_config.json`

### Linux
Edit: `~/.config/Claude/claude_desktop_config.json`

### Configuration Example

```json
{
  "mcpServers": {
    "dockerfile-ai": {
      "command": "dockerfile-ai-mcp",
      "env": {
        "OLLAMA_MODEL": "qwen2.5-coder:7b"
      }
    }
  }
}
```

If you installed the package in a virtual environment, use the full path to the executable:

```json
{
  "mcpServers": {
    "dockerfile-ai": {
      "command": "/path/to/your/venv/bin/dockerfile-ai-mcp",
      "env": {
        "OLLAMA_MODEL": "qwen2.5-coder:7b"
      }
    }
  }
}
```

## Prerequisites

Before using the MCP server, ensure:

1. **Ollama is running**: The server requires Ollama to be running locally on port 11434
   ```bash
   ollama serve
   ```

2. **Model is available**: Make sure the model you want to use is pulled
   ```bash
   ollama pull qwen2.5-coder:7b
   ```

## Usage Examples

Once configured in Claude Desktop, you can use natural language to interact with the Dockerfile AI analyzer:

### Analyze a Dockerfile
```
Can you analyze the Dockerfile at /path/to/Dockerfile for security issues and best practices?
```

### List Saved Analyses
```
Show me all the Dockerfile analyses I've saved
```

### Retrieve a Previous Analysis
```
Get me the analysis file named "Dockerfile_20240115_120000_analysis.md"
```

### Compare Changes
```
Compare the original Dockerfile at /path/to/Dockerfile with the corrected version
```

## Running Standalone

You can also run the MCP server standalone for testing or integration with other MCP clients:

```bash
dockerfile-ai-mcp
```

The server will communicate via stdin/stdout using the MCP protocol.

## Tools Reference

### analyze_dockerfile

Analyzes a Dockerfile and provides recommendations.

**Parameters:**
- `dockerfile_path` (required): Absolute path to the Dockerfile
- `model` (optional): Ollama model to use (default: qwen2.5-coder:7b)
- `save_results` (optional): Whether to save results (default: true)

**Returns:**
```json
{
  "status": "success",
  "original_file": "/path/to/Dockerfile",
  "model_used": "qwen2.5-coder:7b",
  "analysis": "Full analysis text...",
  "corrected_dockerfile": "FROM node:18-alpine\n...",
  "saved_files": {
    "analysis": "/path/to/output/analysis/Dockerfile_timestamp_analysis.md",
    "corrected_dockerfile": "/path/to/output/dockerfiles/Dockerfile_timestamp_corrected.Dockerfile"
  }
}
```

### list_analyses

Lists all saved analyses and corrected Dockerfiles.

**Parameters:** None

**Returns:**
```json
{
  "status": "success",
  "output_directory": "/path/to/output",
  "analyses": [
    {
      "name": "Dockerfile_20240115_120000_analysis.md",
      "path": "/full/path/to/file",
      "size_bytes": 1234,
      "modified": 1705320000.0
    }
  ],
  "corrected_dockerfiles": [...]
}
```

### get_analysis

Retrieves a specific saved analysis or corrected Dockerfile.

**Parameters:**
- `file_name` (required): Name of the file to retrieve

**Returns:**
```json
{
  "status": "success",
  "file_name": "Dockerfile_20240115_120000_analysis.md",
  "file_path": "/full/path/to/file",
  "content": "File contents..."
}
```

## Resources

The MCP server exposes saved files as resources:

- `dockerfile-ai://analysis/{filename}`: Analysis markdown files
- `dockerfile-ai://dockerfile/{filename}`: Corrected Dockerfile files

## Troubleshooting

### Server doesn't start
- Ensure the package is installed correctly: `pip install -e .`
- Check that Ollama is running: `curl http://localhost:11434/api/version`

### Analysis fails
- Verify the Dockerfile path is absolute and accessible
- Check that the Ollama model is available: `ollama list`
- Review server logs for specific error messages

### Claude Desktop doesn't recognize the server
- Verify the configuration file is in the correct location
- Restart Claude Desktop after updating the configuration
- Check the command path is correct (especially for virtual environments)

## Output Directory

Analysis results are saved to:
```
<project-root>/output/
├── analysis/          # Markdown analysis files
└── dockerfiles/       # Corrected Dockerfile files
```

Files are named with timestamps for easy tracking:
- `{original_name}_{timestamp}_analysis.md`
- `{original_name}_{timestamp}_corrected.Dockerfile`

## Environment Variables

- `OLLAMA_MODEL`: Default model to use for analysis (default: qwen2.5-coder:7b)

## Security Considerations

- The MCP server can read any file path provided to it - ensure you only analyze trusted Dockerfiles
- Analysis results may contain sensitive information from your Dockerfiles
- Saved files are stored locally in the output directory

## Contributing

To contribute to the MCP server implementation, please refer to the main [CONTRIBUTING.md](CONTRIBUTING.md) file.

## License

This MCP server is part of the Dockerfile AI project and follows the same MIT License.
