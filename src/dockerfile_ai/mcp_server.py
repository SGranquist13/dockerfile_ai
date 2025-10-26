"""MCP Server for Dockerfile AI Analyzer.

This module implements a Model Context Protocol (MCP) server that exposes
the Dockerfile analysis functionality as tools, resources, and prompts.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
    Prompt,
    PromptMessage,
    GetPromptResult,
)
from pydantic import AnyUrl

from .cli import (
    read_dockerfile,
    query_ollama,
    extract_dockerfile_content,
    save_analysis_file,
    save_dockerfile,
    ensure_output_dirs,
    get_output_dir,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
app = Server("dockerfile-ai")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for Dockerfile analysis."""
    return [
        Tool(
            name="analyze_dockerfile",
            description=(
                "Analyze a Dockerfile and provide AI-powered recommendations for "
                "security, best practices, and optimization. Returns detailed analysis "
                "and a corrected version of the Dockerfile."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dockerfile_path": {
                        "type": "string",
                        "description": "Absolute path to the Dockerfile to analyze",
                    },
                    "model": {
                        "type": "string",
                        "description": "Ollama model to use for analysis (default: qwen2.5-coder:7b)",
                        "default": "qwen2.5-coder:7b",
                    },
                    "save_results": {
                        "type": "boolean",
                        "description": "Whether to save analysis and corrected Dockerfile to output directory",
                        "default": True,
                    },
                },
                "required": ["dockerfile_path"],
            },
        ),
        Tool(
            name="list_analyses",
            description=(
                "List all saved Dockerfile analyses and corrected Dockerfiles "
                "from the output directory."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_analysis",
            description=(
                "Retrieve the content of a specific saved analysis or corrected Dockerfile."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "Name of the analysis or Dockerfile file to retrieve",
                    },
                },
                "required": ["file_name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for Dockerfile analysis."""

    if name == "analyze_dockerfile":
        return await analyze_dockerfile_tool(arguments)
    elif name == "list_analyses":
        return await list_analyses_tool(arguments)
    elif name == "get_analysis":
        return await get_analysis_tool(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def analyze_dockerfile_tool(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Analyze a Dockerfile using AI."""
    dockerfile_path = Path(arguments["dockerfile_path"])
    model = arguments.get("model", "qwen2.5-coder:7b")
    save_results = arguments.get("save_results", True)

    # Validate Dockerfile exists
    if not dockerfile_path.exists():
        return [
            TextContent(
                type="text",
                text=f"Error: Dockerfile not found at {dockerfile_path}",
            )
        ]

    try:
        # Read the Dockerfile
        dockerfile_content = read_dockerfile(dockerfile_path)

        # Analyze with Ollama
        logger.info(f"Analyzing Dockerfile: {dockerfile_path}")
        analysis = await query_ollama(dockerfile_content, model)

        # Extract corrected Dockerfile
        corrected_dockerfile = extract_dockerfile_content(analysis)

        # Save results if requested
        saved_files = {}
        if save_results:
            analysis_path = save_analysis_file(analysis, dockerfile_path.name)
            saved_files["analysis"] = str(analysis_path)

            if corrected_dockerfile:
                dockerfile_output_path = save_dockerfile(
                    corrected_dockerfile, dockerfile_path.name
                )
                saved_files["corrected_dockerfile"] = str(dockerfile_output_path)

        # Build response
        response = {
            "status": "success",
            "original_file": str(dockerfile_path),
            "model_used": model,
            "analysis": analysis,
            "corrected_dockerfile": corrected_dockerfile,
        }

        if saved_files:
            response["saved_files"] = saved_files

        return [
            TextContent(
                type="text",
                text=json.dumps(response, indent=2),
            )
        ]

    except Exception as e:
        logger.error(f"Error analyzing Dockerfile: {e}")
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": str(e),
                }, indent=2),
            )
        ]


async def list_analyses_tool(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """List all saved analyses and corrected Dockerfiles."""
    try:
        analysis_dir, dockerfiles_dir = ensure_output_dirs()

        # Get all analysis files
        analyses = sorted(analysis_dir.glob("*_analysis.md"), key=lambda p: p.stat().st_mtime, reverse=True)

        # Get all corrected Dockerfiles
        dockerfiles = sorted(dockerfiles_dir.glob("*_corrected.Dockerfile"), key=lambda p: p.stat().st_mtime, reverse=True)

        result = {
            "status": "success",
            "output_directory": str(get_output_dir()),
            "analyses": [
                {
                    "name": f.name,
                    "path": str(f),
                    "size_bytes": f.stat().st_size,
                    "modified": f.stat().st_mtime,
                }
                for f in analyses
            ],
            "corrected_dockerfiles": [
                {
                    "name": f.name,
                    "path": str(f),
                    "size_bytes": f.stat().st_size,
                    "modified": f.stat().st_mtime,
                }
                for f in dockerfiles
            ],
        }

        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2),
            )
        ]

    except Exception as e:
        logger.error(f"Error listing analyses: {e}")
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": str(e),
                }, indent=2),
            )
        ]


async def get_analysis_tool(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Get the content of a specific saved analysis or Dockerfile."""
    file_name = arguments["file_name"]

    try:
        analysis_dir, dockerfiles_dir = ensure_output_dirs()

        # Try to find the file in either directory
        file_path = None
        if file_name.endswith("_analysis.md"):
            candidate = analysis_dir / file_name
            if candidate.exists():
                file_path = candidate
        elif file_name.endswith("_corrected.Dockerfile") or file_name.endswith(".Dockerfile"):
            candidate = dockerfiles_dir / file_name
            if candidate.exists():
                file_path = candidate

        if file_path is None:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "error": f"File not found: {file_name}",
                    }, indent=2),
                )
            ]

        # Read and return the file content
        content = file_path.read_text()

        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "file_name": file_name,
                    "file_path": str(file_path),
                    "content": content,
                }, indent=2),
            )
        ]

    except Exception as e:
        logger.error(f"Error reading file {file_name}: {e}")
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": str(e),
                }, indent=2),
            )
        ]


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources (saved analyses and Dockerfiles)."""
    try:
        analysis_dir, dockerfiles_dir = ensure_output_dirs()
        resources = []

        # Add analysis files as resources
        for analysis_file in analysis_dir.glob("*_analysis.md"):
            resources.append(
                Resource(
                    uri=AnyUrl(f"dockerfile-ai://analysis/{analysis_file.name}"),
                    name=f"Analysis: {analysis_file.name}",
                    description=f"Dockerfile analysis saved at {analysis_file.stat().st_mtime}",
                    mimeType="text/markdown",
                )
            )

        # Add corrected Dockerfiles as resources
        for dockerfile in dockerfiles_dir.glob("*_corrected.Dockerfile"):
            resources.append(
                Resource(
                    uri=AnyUrl(f"dockerfile-ai://dockerfile/{dockerfile.name}"),
                    name=f"Corrected: {dockerfile.name}",
                    description=f"Corrected Dockerfile saved at {dockerfile.stat().st_mtime}",
                    mimeType="text/plain",
                )
            )

        return resources

    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        return []


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read a specific resource (analysis or Dockerfile)."""
    try:
        # Parse the URI
        uri_str = str(uri)
        if uri_str.startswith("dockerfile-ai://analysis/"):
            file_name = uri_str.replace("dockerfile-ai://analysis/", "")
            analysis_dir, _ = ensure_output_dirs()
            file_path = analysis_dir / file_name
        elif uri_str.startswith("dockerfile-ai://dockerfile/"):
            file_name = uri_str.replace("dockerfile-ai://dockerfile/", "")
            _, dockerfiles_dir = ensure_output_dirs()
            file_path = dockerfiles_dir / file_name
        else:
            raise ValueError(f"Invalid resource URI: {uri}")

        if not file_path.exists():
            raise FileNotFoundError(f"Resource not found: {file_name}")

        return file_path.read_text()

    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        raise


@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available prompts for Dockerfile analysis."""
    return [
        Prompt(
            name="analyze-dockerfile",
            description="Analyze a Dockerfile for security and best practices",
            arguments=[
                {
                    "name": "dockerfile_path",
                    "description": "Path to the Dockerfile to analyze",
                    "required": True,
                }
            ],
        ),
        Prompt(
            name="review-dockerfile-changes",
            description="Review changes between original and corrected Dockerfile",
            arguments=[
                {
                    "name": "original_path",
                    "description": "Path to the original Dockerfile",
                    "required": True,
                },
                {
                    "name": "corrected_name",
                    "description": "Name of the corrected Dockerfile file",
                    "required": True,
                },
            ],
        ),
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Get a specific prompt for Dockerfile analysis."""

    if name == "analyze-dockerfile":
        if not arguments or "dockerfile_path" not in arguments:
            raise ValueError("dockerfile_path argument is required")

        dockerfile_path = arguments["dockerfile_path"]

        return GetPromptResult(
            description="Analyze this Dockerfile for security and best practices",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Please analyze the Dockerfile at {dockerfile_path} for:\n"
                             "1. Security vulnerabilities and best practices\n"
                             "2. Optimization opportunities (image size, build time)\n"
                             "3. Docker best practices compliance\n"
                             "4. Potential runtime issues\n\n"
                             "Use the analyze_dockerfile tool to perform the analysis.",
                    ),
                )
            ],
        )

    elif name == "review-dockerfile-changes":
        if not arguments or "original_path" not in arguments or "corrected_name" not in arguments:
            raise ValueError("original_path and corrected_name arguments are required")

        original_path = arguments["original_path"]
        corrected_name = arguments["corrected_name"]

        return GetPromptResult(
            description="Review changes between original and corrected Dockerfile",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Please review the changes between:\n"
                             f"- Original: {original_path}\n"
                             f"- Corrected: {corrected_name}\n\n"
                             "Use the get_analysis tool to retrieve the corrected Dockerfile, "
                             "then compare it with the original to highlight key improvements.",
                    ),
                )
            ],
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Run the MCP server."""
    logger.info("Starting Dockerfile AI MCP Server...")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


def run():
    """Entry point for running the MCP server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
