# Dockerfile AI Analyzer

A modern CLI tool that uses Ollama to analyze Dockerfiles and suggest improvements for security, best practices, and optimization.

## Features

- 🤖 AI-powered Dockerfile analysis
- ✨ Beautiful terminal output with typewriter effect
- 📝 Detailed recommendations and improvements
- 🔍 Security and best practices suggestions
- 💾 Save corrected Dockerfile to a file
- 📋 Copy-friendly output option
- 🎯 Configurable Ollama model
- 🔌 MCP (Model Context Protocol) server for integration with AI assistants

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running locally
- A Dockerfile to analyze

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dockerfile-ai.git
cd dockerfile-ai
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Usage

Basic usage:
```bash
dockerfile-ai analyze path/to/your/Dockerfile
```

### Options

- `--output`, `-o`: Save the corrected Dockerfile to a file
  ```bash
  dockerfile-ai analyze Dockerfile -o corrected.Dockerfile
  ```

- `--copy`, `-c`: Display only the corrected Dockerfile for easy copying
  ```bash
  dockerfile-ai analyze Dockerfile --copy
  ```

- `--speed`, `-s`: Adjust the typewriter effect speed (default: 0.001)
  ```bash
  dockerfile-ai analyze Dockerfile --speed 0.01
  ```

- `--model`, `-m`: Specify the Ollama model to use (default: qwen2.5-coder:7b)
  ```bash
  # Recommended model for Dockerfile analysis
  dockerfile-ai analyze Dockerfile --model qwen2.5-coder:7b
  ```

### Environment Variables

- `OLLAMA_MODEL`: Set the default Ollama model to use (default: qwen2.5-coder:7b)
  ```bash
  # Windows
  set OLLAMA_MODEL=qwen2.5-coder:7b
  # Linux/macOS
  export OLLAMA_MODEL=qwen2.5-coder:7b
  ```

## MCP Server

Dockerfile AI can also run as an MCP (Model Context Protocol) server, allowing you to integrate it with AI assistants like Claude Desktop.

### Quick Start

1. Install the package:
   ```bash
   pip install -e .
   ```

2. Configure Claude Desktop to use the MCP server by adding to your `claude_desktop_config.json`:
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

3. Start using it in Claude Desktop:
   ```
   Can you analyze the Dockerfile at /path/to/Dockerfile?
   ```

For detailed setup instructions, see [MCP_SERVER.md](MCP_SERVER.md).

## Example Output

The tool provides:
1. A detailed analysis of your Dockerfile
2. Specific recommendations for improvements
3. A corrected version of the Dockerfile
4. Security and best practices suggestions

## Development

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black src tests
```

4. Lint code:
```bash
ruff check src tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests (`pytest`)
5. Format your code (`black src tests`)
6. Lint your code (`ruff check src tests`)
7. Commit your changes (`git commit -m 'Add some amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Development Guidelines

- Write clear, descriptive commit messages
- Follow the existing code style
- Add tests for new features
- Update documentation for any new features or changes
- Ensure all tests pass before submitting a PR

### Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the version numbers in any relevant files
3. The PR will be merged once you have the sign-off of at least one other developer
4. Make sure all CI checks pass

### Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

### Security

If you discover any security related issues, please email security@example.com instead of using the issue tracker.

## Security Policy

Please see our [Security Policy](SECURITY.md) for details on how to report security vulnerabilities. 