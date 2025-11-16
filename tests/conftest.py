"""Pytest configuration and shared fixtures."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import json


@pytest.fixture
def sample_dockerfile():
    """Fixture providing a sample Dockerfile content."""
    return """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
"""


@pytest.fixture
def bad_dockerfile():
    """Fixture providing a Dockerfile with issues."""
    return """FROM ubuntu:latest

RUN apt-get update && apt-get install -y \\
    python3 \\
    pip

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD python app.py
"""


@pytest.fixture
def sample_analysis():
    """Fixture providing a sample analysis output."""
    return """# Dockerfile Analysis Report

## Summary
Your Dockerfile has been analyzed and improvements have been identified.

## Recommendations
1. Use specific base image version
2. Remove unnecessary packages
3. Use multi-stage builds for smaller images

## Corrected Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
```
"""


@pytest.fixture
def sample_ollama_response():
    """Fixture providing a sample Ollama API response."""
    return """{"response":"# Analysis","done":false}
{"response":"\\n\\nYour Dockerfile has some issues.","done":false}
{"response":"\\n\\n```dockerfile\\nFROM python:3.9-slim\\n```","done":true}
"""


@pytest.fixture
def temp_dockerfile(tmp_path):
    """Fixture creating a temporary Dockerfile."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM python:3.9\nWORKDIR /app\n")
    return dockerfile


@pytest.fixture
def temp_output_dir(tmp_path):
    """Fixture creating a temporary output directory."""
    analysis_dir = tmp_path / "analysis"
    dockerfiles_dir = tmp_path / "dockerfiles"
    analysis_dir.mkdir()
    dockerfiles_dir.mkdir()
    return tmp_path


@pytest.fixture
def mock_ollama_response():
    """Fixture providing a mock Ollama response object."""
    mock = AsyncMock()
    mock.text = """{"response":"Analysis content","done":true}"""
    mock.status_code = 200
    return mock


@pytest.fixture
def mock_httpx_client():
    """Fixture for mocking httpx.AsyncClient."""
    with patch("dockerfile_ai.cli.httpx.AsyncClient") as mock_client:
        yield mock_client
