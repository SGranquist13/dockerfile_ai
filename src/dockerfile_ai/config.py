"""Configuration management for dockerfile_ai."""
import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from pydantic import BaseModel, Field, ConfigDict

from .exceptions import ConfigurationError


class OllamaConfig(BaseModel):
    """Configuration for Ollama connection."""

    model_config = ConfigDict(extra="allow")

    host: str = Field(default="localhost", description="Ollama host")
    port: int = Field(default=11434, description="Ollama port")
    model: str = Field(default="qwen2.5-coder:7b", description="Default Ollama model")
    timeout: int = Field(default=120, description="Request timeout in seconds")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Temperature for generation"
    )
    top_p: float = Field(
        default=0.9, ge=0.0, le=1.0, description="Top-p for nucleus sampling"
    )
    max_tokens: int = Field(
        default=4000, ge=1, description="Maximum tokens in response"
    )

    @property
    def url(self) -> str:
        """Get the Ollama API URL."""
        return f"http://{self.host}:{self.port}"


class OutputConfig(BaseModel):
    """Configuration for output handling."""

    model_config = ConfigDict(extra="allow")

    save_analysis: bool = Field(
        default=True, description="Whether to save analysis to file"
    )
    save_dockerfile: bool = Field(
        default=True, description="Whether to save corrected Dockerfile"
    )
    output_dir: Optional[str] = Field(
        default=None, description="Custom output directory"
    )
    copy_mode: bool = Field(
        default=False, description="Display only corrected Dockerfile"
    )
    typewriter_speed: float = Field(
        default=0.001, description="Speed of typewriter effect"
    )


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    model_config = ConfigDict(extra="allow")

    level: str = Field(default="INFO", description="Log level (DEBUG, INFO, WARNING, ERROR)")
    file_logging: bool = Field(default=False, description="Enable file logging")
    verbose: bool = Field(default=False, description="Verbose output")
    log_file: Optional[str] = Field(default=None, description="Custom log file path")


class DockerfileAIConfig(BaseModel):
    """Main configuration for dockerfile_ai."""

    model_config = ConfigDict(extra="allow")

    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def get_config_path() -> Path:
    """Get the configuration file path.

    Returns:
        Path to .dockerfileai.yaml in home directory
    """
    return Path.home() / ".dockerfileai.yaml"


def load_config_file(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        path: Path to config file (default: ~/.dockerfileai.yaml)

    Returns:
        Configuration dictionary

    Raises:
        ConfigurationError: If file cannot be read or parsed
    """
    if path is None:
        path = get_config_path()

    if not path.exists():
        return {}

    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
            return config or {}
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config file {path}: {str(e)}")
    except Exception as e:
        raise ConfigurationError(f"Error reading config file {path}: {str(e)}")


def load_env_config() -> Dict[str, Any]:
    """Load configuration from environment variables.

    Returns:
        Configuration dictionary from environment variables
    """
    config = {}

    # Ollama configuration
    if os.getenv("OLLAMA_HOST"):
        config.setdefault("ollama", {})["host"] = os.getenv("OLLAMA_HOST")
    if os.getenv("OLLAMA_PORT"):
        config.setdefault("ollama", {})["port"] = int(os.getenv("OLLAMA_PORT"))
    if os.getenv("OLLAMA_MODEL"):
        config.setdefault("ollama", {})["model"] = os.getenv("OLLAMA_MODEL")
    if os.getenv("OLLAMA_TIMEOUT"):
        config.setdefault("ollama", {})["timeout"] = int(os.getenv("OLLAMA_TIMEOUT"))
    if os.getenv("OLLAMA_TEMPERATURE"):
        config.setdefault("ollama", {})["temperature"] = float(
            os.getenv("OLLAMA_TEMPERATURE")
        )

    # Output configuration
    if os.getenv("DOCKERFILE_AI_SAVE_ANALYSIS"):
        config.setdefault("output", {})["save_analysis"] = (
            os.getenv("DOCKERFILE_AI_SAVE_ANALYSIS").lower() == "true"
        )
    if os.getenv("DOCKERFILE_AI_COPY_MODE"):
        config.setdefault("output", {})["copy_mode"] = (
            os.getenv("DOCKERFILE_AI_COPY_MODE").lower() == "true"
        )
    if os.getenv("DOCKERFILE_AI_OUTPUT_DIR"):
        config.setdefault("output", {})["output_dir"] = os.getenv(
            "DOCKERFILE_AI_OUTPUT_DIR"
        )

    # Logging configuration
    if os.getenv("DOCKERFILE_AI_LOG_LEVEL"):
        config.setdefault("logging", {})["level"] = os.getenv(
            "DOCKERFILE_AI_LOG_LEVEL"
        )
    if os.getenv("DOCKERFILE_AI_LOG_FILE"):
        config.setdefault("logging", {})["log_file"] = os.getenv(
            "DOCKERFILE_AI_LOG_FILE"
        )

    return config


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple configuration dictionaries.

    Args:
        *configs: Configuration dictionaries to merge

    Returns:
        Merged configuration dictionary
    """
    result = {}
    for config in configs:
        for key, value in config.items():
            if isinstance(value, dict) and key in result:
                result[key] = {**result[key], **value}
            else:
                result[key] = value
    return result


def load_configuration(
    config_file: Optional[Path] = None, override: Optional[Dict[str, Any]] = None
) -> DockerfileAIConfig:
    """Load and merge all configuration sources.

    Args:
        config_file: Optional custom config file path
        override: Optional override configuration dictionary

    Returns:
        Merged DockerfileAIConfig instance

    Raises:
        ConfigurationError: If configuration is invalid
    """
    # Load from file, environment, and overrides
    file_config = load_config_file(config_file)
    env_config = load_env_config()
    override_config = override or {}

    # Merge configs (file < environment < override)
    merged = merge_configs(file_config, env_config, override_config)

    try:
        return DockerfileAIConfig(**merged)
    except Exception as e:
        raise ConfigurationError(f"Invalid configuration: {str(e)}")


def save_config(config: DockerfileAIConfig, path: Optional[Path] = None) -> Path:
    """Save configuration to YAML file.

    Args:
        config: Configuration to save
        path: Path to save to (default: ~/.dockerfileai.yaml)

    Returns:
        Path where configuration was saved

    Raises:
        ConfigurationError: If file cannot be written
    """
    if path is None:
        path = get_config_path()

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(config.model_dump(exclude_defaults=True), f)
        return path
    except Exception as e:
        raise ConfigurationError(f"Error saving config to {path}: {str(e)}")


def create_sample_config() -> str:
    """Create a sample configuration file content.

    Returns:
        Sample YAML configuration as string
    """
    sample_config = {
        "ollama": {
            "host": "localhost",
            "port": 11434,
            "model": "qwen2.5-coder:7b",
            "timeout": 120,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 4000,
        },
        "output": {
            "save_analysis": True,
            "save_dockerfile": True,
            "copy_mode": False,
            "typewriter_speed": 0.001,
        },
        "logging": {
            "level": "INFO",
            "file_logging": False,
            "verbose": False,
        },
    }
    return yaml.dump(sample_config, default_flow_style=False)
