"""Custom exception classes for dockerfile_ai."""


class DockerfileAIException(Exception):
    """Base exception for all dockerfile_ai errors."""

    pass


class DockerfileError(DockerfileAIException):
    """Exception raised when there's an error reading or processing a Dockerfile."""

    pass


class OllamaConnectionError(DockerfileAIException):
    """Exception raised when unable to connect to Ollama service."""

    pass


class OllamaError(DockerfileAIException):
    """Exception raised when Ollama API returns an error."""

    pass


class OllamaResponseError(OllamaError):
    """Exception raised when Ollama response is invalid or empty."""

    pass


class ConfigurationError(DockerfileAIException):
    """Exception raised when there's a configuration issue."""

    pass


class OutputError(DockerfileAIException):
    """Exception raised when there's an error saving output files."""

    pass


class ValidationError(DockerfileAIException):
    """Exception raised when input validation fails."""

    pass
