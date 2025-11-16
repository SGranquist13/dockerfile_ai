"""Tests for the CLI module."""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import json
from datetime import datetime
from typer.testing import CliRunner

from dockerfile_ai import cli
from dockerfile_ai.cli import app


runner = CliRunner()


class TestReadDockerfile:
    """Tests for read_dockerfile function."""

    def test_read_existing_dockerfile(self, temp_dockerfile):
        """Test reading an existing Dockerfile."""
        content = cli.read_dockerfile(temp_dockerfile)
        assert isinstance(content, str)
        assert "FROM python:3.9" in content

    def test_read_nonexistent_dockerfile(self):
        """Test reading a nonexistent file raises exception."""
        fake_path = Path("/nonexistent/Dockerfile")
        with pytest.raises(Exception):
            cli.read_dockerfile(fake_path)

    def test_read_dockerfile_returns_string(self, temp_dockerfile):
        """Test that read_dockerfile returns a string."""
        result = cli.read_dockerfile(temp_dockerfile)
        assert isinstance(result, str)

    def test_read_dockerfile_preserves_content(self, temp_dockerfile):
        """Test that read_dockerfile preserves exact content."""
        original = temp_dockerfile.read_text()
        result = cli.read_dockerfile(temp_dockerfile)
        assert result == original


class TestExtractDockerfileContent:
    """Tests for extract_dockerfile_content function."""

    def test_extract_from_markdown_codeblock(self):
        """Test extracting Dockerfile from markdown code block."""
        text = """# Analysis

Here's the improved Dockerfile:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

This is much better!
"""
        result = cli.extract_dockerfile_content(text)
        assert "FROM python:3.9-slim" in result
        assert "WORKDIR /app" in result

    def test_extract_without_dockerfile_label(self):
        """Test extracting Dockerfile without 'dockerfile' label."""
        text = """
```
FROM ubuntu:20.04
RUN apt-get update
```
"""
        result = cli.extract_dockerfile_content(text)
        # Should not match because it doesn't start with FROM
        # Wait, let me check - the pattern looks for "dockerfile" label
        # Actually the regex allows optional dockerfile label
        assert "FROM ubuntu:20.04" in result

    def test_extract_invalid_no_from(self):
        """Test extracting text that doesn't start with FROM."""
        text = """
```dockerfile
RUN apt-get update
WORKDIR /app
```
"""
        result = cli.extract_dockerfile_content(text)
        # Should return empty string since it doesn't start with FROM
        assert result == ""

    def test_extract_multiline_dockerfile(self):
        """Test extracting multiline Dockerfile."""
        text = """```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "app.py"]
```"""
        result = cli.extract_dockerfile_content(text)
        assert "FROM python:3.9" in result
        assert "WORKDIR /app" in result
        assert "EXPOSE 8000" in result

    def test_extract_no_codeblock(self):
        """Test extracting from text without code block."""
        text = "This is just plain text with no Dockerfile"
        result = cli.extract_dockerfile_content(text)
        assert result == ""

    def test_extract_with_whitespace(self):
        """Test extracting with leading/trailing whitespace."""
        text = """
```dockerfile

FROM python:3.9
WORKDIR /app

```
"""
        result = cli.extract_dockerfile_content(text)
        assert "FROM python:3.9" in result
        assert result.startswith("FROM")


class TestCreateHeader:
    """Tests for create_header function."""

    def test_create_header_returns_panel(self):
        """Test that create_header returns a Panel."""
        from rich.panel import Panel
        result = cli.create_header()
        assert isinstance(result, Panel)

    def test_create_header_has_cyan_style(self):
        """Test that header uses cyan styling."""
        result = cli.create_header()
        assert result.border_style == "cyan"


class TestCreateWarning:
    """Tests for create_warning function."""

    def test_create_warning_returns_panel(self):
        """Test that create_warning returns a Panel."""
        from rich.panel import Panel
        result = cli.create_warning()
        assert isinstance(result, Panel)

    def test_create_warning_has_yellow_style(self):
        """Test that warning uses yellow styling."""
        result = cli.create_warning()
        assert result.border_style == "yellow"

    def test_create_warning_contains_important_text(self):
        """Test that warning contains important notice."""
        result = cli.create_warning()
        # Check that the panel was created with title
        assert result.title is not None


class TestGetOutputDir:
    """Tests for get_output_dir function."""

    def test_get_output_dir_returns_path(self):
        """Test that get_output_dir returns a Path."""
        result = cli.get_output_dir()
        assert isinstance(result, Path)

    def test_get_output_dir_ends_with_output(self):
        """Test that output dir path ends with 'output'."""
        result = cli.get_output_dir()
        assert result.name == "output"


class TestEnsureOutputDirs:
    """Tests for ensure_output_dirs function."""

    def test_ensure_output_dirs_returns_tuple(self):
        """Test that ensure_output_dirs returns a tuple."""
        result = cli.ensure_output_dirs()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_ensure_output_dirs_creates_directories(self, temp_output_dir, monkeypatch):
        """Test that ensure_output_dirs creates directories."""
        monkeypatch.setattr(cli, "get_output_dir", lambda: temp_output_dir)
        analysis_dir, dockerfiles_dir = cli.ensure_output_dirs()

        assert (temp_output_dir / "analysis").exists()
        assert (temp_output_dir / "dockerfiles").exists()

    def test_ensure_output_dirs_idempotent(self, temp_output_dir, monkeypatch):
        """Test that ensure_output_dirs can be called multiple times."""
        monkeypatch.setattr(cli, "get_output_dir", lambda: temp_output_dir)
        result1 = cli.ensure_output_dirs()
        result2 = cli.ensure_output_dirs()

        assert result1 == result2


class TestSaveAnalysisFile:
    """Tests for save_analysis_file function."""

    def test_save_analysis_file_creates_file(self, temp_output_dir, monkeypatch):
        """Test that save_analysis_file creates a file."""
        monkeypatch.setattr(cli, "get_output_dir", lambda: temp_output_dir)

        analysis = "# Analysis Report\nSome analysis content"
        result = cli.save_analysis_file(analysis, "Dockerfile")

        assert result.exists()
        assert result.read_text() == analysis

    def test_save_analysis_file_includes_timestamp(self, temp_output_dir, monkeypatch):
        """Test that saved file includes timestamp in name."""
        monkeypatch.setattr(cli, "get_output_dir", lambda: temp_output_dir)

        result = cli.save_analysis_file("analysis", "Dockerfile")
        assert "_analysis.md" in result.name
        # Should have timestamp pattern YYYYMMDD_HHMMSS
        import re
        pattern = r"\d{8}_\d{6}"
        assert re.search(pattern, result.name)

    def test_save_analysis_file_returns_path(self, temp_output_dir, monkeypatch):
        """Test that save_analysis_file returns a Path."""
        monkeypatch.setattr(cli, "get_output_dir", lambda: temp_output_dir)

        result = cli.save_analysis_file("analysis", "Dockerfile")
        assert isinstance(result, Path)

    def test_save_analysis_file_in_analysis_dir(self, temp_output_dir, monkeypatch):
        """Test that file is saved in analysis directory."""
        monkeypatch.setattr(cli, "get_output_dir", lambda: temp_output_dir)

        result = cli.save_analysis_file("analysis", "Dockerfile")
        assert result.parent.name == "analysis"


class TestSaveDockerfile:
    """Tests for save_dockerfile function."""

    def test_save_dockerfile_creates_file(self, temp_output_dir, monkeypatch):
        """Test that save_dockerfile creates a file."""
        monkeypatch.setattr(cli, "get_output_dir", lambda: temp_output_dir)

        dockerfile = "FROM python:3.9\nWORKDIR /app"
        result = cli.save_dockerfile(dockerfile, "Dockerfile")

        assert result.exists()
        assert result.read_text() == dockerfile

    def test_save_dockerfile_includes_corrected_label(self, temp_output_dir, monkeypatch):
        """Test that saved dockerfile includes '_corrected' in name."""
        monkeypatch.setattr(cli, "get_output_dir", lambda: temp_output_dir)

        result = cli.save_dockerfile("content", "Dockerfile")
        assert "_corrected" in result.name
        assert result.name.endswith(".Dockerfile")

    def test_save_dockerfile_returns_path(self, temp_output_dir, monkeypatch):
        """Test that save_dockerfile returns a Path."""
        monkeypatch.setattr(cli, "get_output_dir", lambda: temp_output_dir)

        result = cli.save_dockerfile("content", "Dockerfile")
        assert isinstance(result, Path)

    def test_save_dockerfile_in_dockerfiles_dir(self, temp_output_dir, monkeypatch):
        """Test that file is saved in dockerfiles directory."""
        monkeypatch.setattr(cli, "get_output_dir", lambda: temp_output_dir)

        result = cli.save_dockerfile("content", "Dockerfile")
        assert result.parent.name == "dockerfiles"


class TestQueryOllama:
    """Tests for query_ollama async function."""

    @pytest.mark.asyncio
    async def test_query_ollama_success(self):
        """Test successful Ollama query."""
        mock_response = AsyncMock()
        mock_response.text = '{"response": "analysis", "done": true}\n'
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch("dockerfile_ai.cli.httpx.AsyncClient") as mock_client_class:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_instance.post.return_value = mock_response
            mock_client_class.return_value = mock_instance

            result = await cli.query_ollama("FROM python:3.9", "test-model")
            assert isinstance(result, str)
            assert "analysis" in result

    @pytest.mark.asyncio
    async def test_query_ollama_empty_response(self):
        """Test that empty Ollama response raises ValueError."""
        mock_response = AsyncMock()
        mock_response.text = ""
        mock_response.raise_for_status = MagicMock()

        with patch("dockerfile_ai.cli.httpx.AsyncClient") as mock_client_class:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_instance.post.return_value = mock_response
            mock_client_class.return_value = mock_instance

            with pytest.raises(Exception):  # Will exit with typer.Exit
                await cli.query_ollama("FROM python:3.9", "test-model")

    @pytest.mark.asyncio
    async def test_query_ollama_multiline_response(self):
        """Test handling multiline JSON responses."""
        mock_response = AsyncMock()
        mock_response.text = '{"response": "line1", "done": false}\n{"response": "line2", "done": true}\n'
        mock_response.raise_for_status = MagicMock()

        with patch("dockerfile_ai.cli.httpx.AsyncClient") as mock_client_class:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_instance.post.return_value = mock_response
            mock_client_class.return_value = mock_instance

            result = await cli.query_ollama("FROM python:3.9", "test-model")
            assert "line1" in result
            assert "line2" in result


class TestDisplayTypewriter:
    """Tests for display_typewriter function."""

    def test_display_typewriter_with_short_text(self, capsys):
        """Test display_typewriter with short text."""
        # This is tricky because it uses Live display
        # We'll just ensure it doesn't crash
        cli.display_typewriter("Short text", speed=0.0, copyable=False)
        # Just ensure it completes without error

    def test_display_typewriter_copyable_mode(self, capsys):
        """Test display_typewriter in copyable mode."""
        text = """Analysis content

```dockerfile
FROM python:3.9
WORKDIR /app
```
"""
        cli.display_typewriter(text, copyable=True)
        # Should complete without error


class TestCLICommand:
    """Integration tests for the analyze CLI command."""

    def test_analyze_command_with_valid_dockerfile(self, temp_dockerfile):
        """Test analyze command with a valid Dockerfile."""
        with patch("dockerfile_ai.cli.query_ollama") as mock_query:
            # Mock the async function
            async def mock_async(*args, **kwargs):
                return "# Analysis\n\n```dockerfile\nFROM python:3.9\n```"

            mock_query.side_effect = mock_async

            result = runner.invoke(app, [str(temp_dockerfile)])
            # Should complete without error
            assert result.exit_code == 0

    def test_analyze_command_nonexistent_file(self):
        """Test analyze command with nonexistent file."""
        result = runner.invoke(app, ["/nonexistent/Dockerfile"])
        # Typer should handle the validation
        assert result.exit_code != 0

    def test_analyze_command_with_model_option(self, temp_dockerfile):
        """Test analyze command with custom model."""
        with patch("dockerfile_ai.cli.query_ollama") as mock_query:
            async def mock_async(*args, **kwargs):
                return "# Analysis\n\n```dockerfile\nFROM python:3.9\n```"

            mock_query.side_effect = mock_async

            result = runner.invoke(
                app,
                [str(temp_dockerfile), "--model", "custom-model:7b"]
            )
            assert result.exit_code == 0


class TestOllamaResponse:
    """Tests for OllamaResponse model."""

    def test_ollama_response_valid(self):
        """Test OllamaResponse with valid data."""
        response = cli.OllamaResponse(response="test", done=True)
        assert response.response == "test"
        assert response.done is True

    def test_ollama_response_fields(self):
        """Test OllamaResponse has required fields."""
        response = cli.OllamaResponse(response="test", done=False)
        assert hasattr(response, "response")
        assert hasattr(response, "done")
