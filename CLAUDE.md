# CLAUDE.md - AI Assistant Guide for Dockerfile AI Analyzer

This document provides comprehensive guidance for AI assistants working with the Dockerfile AI Analyzer codebase.

## Project Overview

**Dockerfile AI Analyzer** is a modern CLI tool that uses Ollama to analyze Dockerfiles and suggest improvements for security, best practices, and optimization.

### Key Features
- AI-powered Dockerfile analysis using Ollama
- Beautiful terminal output with Rich library
- Typewriter effect for streaming analysis results
- Security and best practices recommendations
- Configurable AI models
- Automatic saving of analysis reports and corrected Dockerfiles
- Multiple output formats (detailed analysis, copy-friendly)

### Technology Stack
- **Language**: Python 3.9+
- **CLI Framework**: Typer
- **Terminal UI**: Rich
- **HTTP Client**: httpx (async)
- **Data Validation**: Pydantic
- **AI Backend**: Ollama (local LLM)
- **Build System**: Hatchling
- **Package Manager**: Rye (optional)

## Repository Structure

```
dockerfile_ai/
├── src/dockerfile_ai/         # Main source code
│   ├── __init__.py            # Package initialization (version: 0.1.0)
│   ├── __main__.py            # Entry point for module execution
│   ├── cli.py                 # Main CLI application logic
│   └── prompts.py             # Prompt management and formatting
├── ai/prompts/                # AI prompt templates
│   ├── v1                     # Basic prompt template
│   └── v2                     # Advanced prompt template (default)
├── example/                   # Example Dockerfiles
│   └── bad_dockerfile         # Intentionally bad Dockerfile for testing
├── output/                    # Generated output (gitignored)
│   ├── analysis/              # Analysis markdown files
│   └── dockerfiles/           # Corrected Dockerfiles
├── pyproject.toml             # Project configuration and dependencies
├── README.md                  # User documentation
├── SECURITY.md                # Security policy
├── LICENSE                    # MIT License
└── .gitignore                 # Git ignore rules
```

## Code Architecture

### Main Components

#### 1. CLI Module (`src/dockerfile_ai/cli.py`)

The core application logic with these key functions:

- **`analyze()` command**: Main CLI command that orchestrates the analysis workflow
  - Arguments: `dockerfile` (path to analyze)
  - Options: `--output/-o`, `--copy/-c`, `--speed/-s`, `--model/-m`, `--save-analysis`

- **`query_ollama()`**: Async function that communicates with Ollama API
  - Uses httpx async client
  - Handles streaming responses from Ollama
  - Default endpoint: `http://localhost:11434/api/generate`
  - Temperature: 0.7, Top-p: 0.9, Max tokens: 4000

- **`read_dockerfile()`**: Reads Dockerfile content with error handling

- **`extract_dockerfile_content()`**: Extracts corrected Dockerfile from AI response
  - Uses regex to find triple-quoted code blocks
  - Validates content starts with `FROM`

- **`display_typewriter()`**: Creates typewriter effect for terminal output
  - Uses Rich's Live display
  - Configurable speed parameter
  - Updates display every 50ms to prevent lag

- **`save_analysis_file()`**: Saves analysis to `output/analysis/`
  - Filename format: `{dockerfile_name}_{timestamp}_analysis.md`

- **`save_dockerfile()`**: Saves corrected Dockerfile to `output/dockerfiles/`
  - Filename format: `{dockerfile_name}_{timestamp}_corrected.Dockerfile`

- **UI Components**:
  - `create_header()`: Creates branded header panel
  - `create_warning()`: Creates AI output warning panel

#### 2. Prompts Module (`src/dockerfile_ai/prompts.py`)

Manages AI prompt templates:

- **`get_prompt_path()`**: Returns path to prompts directory
- **`read_prompt()`**: Reads prompt template (default: v2)
- **`format_prompt()`**: Combines template with Dockerfile content

### AI Prompt Versions

#### V1 Prompt
Basic analysis covering:
- Validity
- Security
- Efficiency
- Readability
- Maintainability

Output format: Analysis Report + Updated Dockerfile

#### V2 Prompt (Default)
Advanced analysis as an "Elite Docker and Cloud-Native Security Architect":
- Comprehensive security posture analysis
- BuildKit features consideration
- Multi-stage build optimization
- Layer caching strategies
- Attack surface reduction
- Health checks
- Secrets management
- Performance optimization

Output format: Comprehensive Analysis & Recommendations + Optimized & Hardened Dockerfile

## Development Workflows

### Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd dockerfile-ai

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install in development mode
pip install -e .

# Install with dev dependencies (if available)
pip install -e ".[dev]"
```

### Running the Tool

```bash
# Basic analysis
dockerfile-ai analyze path/to/Dockerfile

# With custom model
dockerfile-ai analyze Dockerfile --model qwen2.5-coder:7b

# Save to specific output
dockerfile-ai analyze Dockerfile -o corrected.Dockerfile

# Copy-friendly output (no typewriter effect)
dockerfile-ai analyze Dockerfile --copy

# Adjust typewriter speed
dockerfile-ai analyze Dockerfile --speed 0.01
```

### Testing

```bash
# Run tests (when test suite exists)
pytest

# With coverage
pytest --cov=src/dockerfile_ai
```

### Code Quality

```bash
# Format code
black src tests

# Lint code
ruff check src tests

# Type checking (if mypy is configured)
mypy src
```

## Code Conventions

### Python Style
- **Formatter**: Black (line length: 88)
- **Linter**: Ruff (target: Python 3.9+)
- **Type Hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

### Import Organization
1. Standard library imports
2. Third-party imports
3. Local application imports

Example from `cli.py`:
```python
import typer
from pathlib import Path
from rich.console import Console
# ... other imports
from .prompts import format_prompt
```

### Async/Await
- Use async/await for I/O operations (HTTP requests)
- Use `httpx.AsyncClient` for Ollama API calls
- Run async code with `asyncio.run()`

### Error Handling
- Use try-except blocks for I/O operations
- Display user-friendly error messages with Rich
- Use `typer.Exit(1)` for fatal errors

### Configuration
- Use environment variables for defaults (e.g., `OLLAMA_MODEL`)
- Provide CLI options to override environment variables
- Default model: `qwen2.5-coder:7b`

## Key Design Patterns

### 1. Single Responsibility
Each function has a clear, single purpose:
- `read_dockerfile()` only reads files
- `query_ollama()` only handles API communication
- `display_typewriter()` only handles display

### 2. Path Management
Use `pathlib.Path` for all file operations:
```python
from pathlib import Path
file_path = Path(__file__).parent / "file.txt"
content = file_path.read_text()
```

### 3. Rich Terminal UI
Consistent use of Rich components:
- `Console` for output
- `Panel` for bordered content
- `Markdown` for formatted text
- `Progress` for loading indicators
- `Live` for dynamic updates

### 4. Pydantic Models
Use Pydantic for data validation:
```python
class OllamaResponse(BaseModel):
    response: str
    done: bool
```

## Common Development Tasks

### Adding a New CLI Command

1. Add command function to `cli.py`:
```python
@app.command()
def new_command(
    arg: str = typer.Argument(..., help="Description"),
    option: bool = typer.Option(False, "--flag", "-f", help="Description")
):
    """Command description."""
    # Implementation
```

2. Update README.md with new command documentation

### Creating a New Prompt Template

1. Create new file in `ai/prompts/` (e.g., `v3`)
2. Write prompt following the two-section format:
   - Section 1: Analysis/Recommendations
   - Section 2: Optimized Dockerfile
3. Update `prompts.py` if needed for special handling

### Modifying Output Format

1. Edit `display_typewriter()` in `cli.py`
2. Update Rich components (Panel, Markdown, etc.)
3. Test with various Dockerfile sizes
4. Consider performance impact on typewriter effect

### Changing Ollama Parameters

Edit `query_ollama()` in `cli.py`:
```python
json={
    "model": model,
    "prompt": prompt,
    "temperature": 0.7,  # Modify as needed
    "top_p": 0.9,        # Modify as needed
    "max_tokens": 4000   # Modify as needed
}
```

### Adding New Analysis Dimensions

1. Update prompt template in `ai/prompts/v2` (or create v3)
2. Test with example Dockerfiles
3. Validate output format remains consistent
4. Update documentation

## Git Workflow

### Branch Structure
- Development branches: `claude/claude-md-*` (for Claude AI development)
- Feature branches: `feature/feature-name`
- Bug fix branches: `bugfix/issue-description`

### Commit Messages
Follow conventional commit format:
```
type: Brief description

Detailed explanation if needed
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Build/tooling changes

### Pre-commit Checks
Before committing:
1. Run `black src tests`
2. Run `ruff check src tests`
3. Ensure tests pass (if available)
4. Update documentation if needed

## Security Considerations

### Input Validation
- Validate Dockerfile paths before reading
- Use Pydantic for API response validation
- Sanitize file paths to prevent directory traversal

### Secrets Management
- Never hardcode API keys or secrets
- Use environment variables for sensitive configuration
- Keep output directory gitignored

### Ollama Connection
- Default to localhost only
- No remote Ollama connections without explicit configuration
- Timeout set to 120 seconds to prevent hanging

### AI Output Warning
Always display warning panel reminding users:
- AI output should be reviewed before implementation
- Verify security implications
- Test changes in safe environment

## Output Management

### Directory Structure
```
output/
├── analysis/                    # Timestamped analysis reports
│   └── {name}_{timestamp}_analysis.md
└── dockerfiles/                 # Timestamped corrected Dockerfiles
    └── {name}_{timestamp}_corrected.Dockerfile
```

### File Naming Convention
- Format: `{original_name}_{YYYYMMDD_HHMMSS}_{type}.{extension}`
- Example: `bad_dockerfile_20241116_143022_analysis.md`
- Example: `Dockerfile_20241116_143022_corrected.Dockerfile`

### Gitignore
The `output/` directory is gitignored to prevent committing generated files.

## Dependencies

### Production Dependencies
- `typer>=0.9.0` - CLI framework
- `rich>=13.7.0` - Terminal formatting
- `pydantic>=2.6.1` - Data validation
- `httpx>=0.26.0` - Async HTTP client
- `python-dotenv>=1.0.0` - Environment variable loading

### Development Dependencies
- `pytest>=7.4.0` - Testing framework
- `black>=23.12.0` - Code formatter
- `ruff>=0.1.14` - Linter

## Performance Considerations

### Typewriter Effect
- Update interval: 50ms (0.05 seconds)
- Default speed: 0.001 (adjustable with `--speed`)
- Buffered updates to prevent terminal lag

### Async HTTP
- Uses httpx AsyncClient for non-blocking Ollama requests
- Timeout: 120 seconds
- Streaming response handling

### Memory Management
- Processes Ollama responses line-by-line
- Validates responses before storing
- Cleans up temporary data

## Testing Strategy

### Test Categories
1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test CLI commands end-to-end
3. **Validation Tests**: Test with various Dockerfile formats

### Example Test Locations
- Use `example/bad_dockerfile` for testing analysis
- Create test fixtures for edge cases
- Mock Ollama responses for offline testing

## Troubleshooting Guide

### Common Issues

**Ollama Connection Error**
- Ensure Ollama is running: `ollama serve`
- Check if running on port 11434
- Verify model is available: `ollama list`

**Empty Response Error**
- Model may not be installed: `ollama pull qwen2.5-coder:7b`
- Increase timeout if model is slow
- Check Ollama logs

**Import Errors**
- Ensure package is installed: `pip install -e .`
- Activate virtual environment
- Check Python version (requires 3.9+)

**Permission Errors**
- Check Dockerfile read permissions
- Ensure output directory is writable
- May need to create `output/` directory manually

## Future Enhancement Ideas

### Potential Features
- Support for multiple Dockerfile analysis in batch
- Comparison mode (before/after)
- Integration with CI/CD pipelines
- Docker image scanning integration
- Custom prompt templates from user files
- JSON output format for programmatic use
- Diff view for changes
- Web UI option

### Code Improvements
- Add comprehensive test suite
- Implement logging system
- Add configuration file support (.dockerfileai.yaml)
- Create plugin system for custom analyzers
- Add caching for repeated analyses

## Resources

### External Documentation
- [Ollama Documentation](https://ollama.ai/docs)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

### Internal Files
- `README.md` - User-facing documentation
- `SECURITY.md` - Security policy and reporting
- `pyproject.toml` - Project configuration
- `ai/prompts/v2` - Current prompt template

## Version Information

- **Current Version**: 0.1.0
- **Python Version**: 3.9+
- **License**: MIT

## Contributing Guidelines

1. **Fork the repository**
2. **Create a feature branch** from the appropriate base branch
3. **Make changes** following code conventions
4. **Test thoroughly** with various Dockerfiles
5. **Format code** with Black
6. **Lint code** with Ruff
7. **Commit** with clear messages
8. **Push** to your branch
9. **Create Pull Request** with detailed description

### PR Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated (when applicable)
- [ ] Documentation updated (README, CLAUDE.md)
- [ ] All tests pass
- [ ] No security vulnerabilities introduced
- [ ] Commit messages are clear and descriptive

---

**Last Updated**: 2025-11-16
**Document Version**: 1.0
**Maintained By**: Project Contributors
