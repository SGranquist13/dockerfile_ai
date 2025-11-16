"""Tests for the configuration module."""
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import yaml

from dockerfile_ai import config
from dockerfile_ai.exceptions import ConfigurationError


class TestOllamaConfig:
    """Tests for OllamaConfig class."""

    def test_ollama_config_defaults(self):
        """Test OllamaConfig with defaults."""
        cfg = config.OllamaConfig()
        assert cfg.host == "localhost"
        assert cfg.port == 11434
        assert cfg.model == "qwen2.5-coder:7b"
        assert cfg.timeout == 120
        assert cfg.temperature == 0.7
        assert cfg.top_p == 0.9
        assert cfg.max_tokens == 4000

    def test_ollama_config_custom_values(self):
        """Test OllamaConfig with custom values."""
        cfg = config.OllamaConfig(
            host="127.0.0.1",
            port=8080,
            model="custom:7b",
            timeout=60,
        )
        assert cfg.host == "127.0.0.1"
        assert cfg.port == 8080
        assert cfg.model == "custom:7b"
        assert cfg.timeout == 60

    def test_ollama_config_url_property(self):
        """Test OllamaConfig URL property."""
        cfg = config.OllamaConfig(host="127.0.0.1", port=8080)
        assert cfg.url == "http://127.0.0.1:8080"

    def test_ollama_config_default_url(self):
        """Test OllamaConfig default URL."""
        cfg = config.OllamaConfig()
        assert cfg.url == "http://localhost:11434"

    def test_ollama_config_temperature_validation(self):
        """Test OllamaConfig temperature validation."""
        # Valid temperatures
        cfg = config.OllamaConfig(temperature=0.0)
        assert cfg.temperature == 0.0

        cfg = config.OllamaConfig(temperature=2.0)
        assert cfg.temperature == 2.0


class TestOutputConfig:
    """Tests for OutputConfig class."""

    def test_output_config_defaults(self):
        """Test OutputConfig with defaults."""
        cfg = config.OutputConfig()
        assert cfg.save_analysis is True
        assert cfg.save_dockerfile is True
        assert cfg.copy_mode is False
        assert cfg.typewriter_speed == 0.001

    def test_output_config_custom_values(self):
        """Test OutputConfig with custom values."""
        cfg = config.OutputConfig(
            save_analysis=False,
            copy_mode=True,
            typewriter_speed=0.01,
        )
        assert cfg.save_analysis is False
        assert cfg.copy_mode is True
        assert cfg.typewriter_speed == 0.01


class TestLoggingConfig:
    """Tests for LoggingConfig class."""

    def test_logging_config_defaults(self):
        """Test LoggingConfig with defaults."""
        cfg = config.LoggingConfig()
        assert cfg.level == "INFO"
        assert cfg.file_logging is False
        assert cfg.verbose is False

    def test_logging_config_custom_values(self):
        """Test LoggingConfig with custom values."""
        cfg = config.LoggingConfig(
            level="DEBUG",
            file_logging=True,
            verbose=True,
        )
        assert cfg.level == "DEBUG"
        assert cfg.file_logging is True
        assert cfg.verbose is True


class TestDockerfileAIConfig:
    """Tests for DockerfileAIConfig class."""

    def test_dockerfileai_config_defaults(self):
        """Test DockerfileAIConfig with defaults."""
        cfg = config.DockerfileAIConfig()
        assert isinstance(cfg.ollama, config.OllamaConfig)
        assert isinstance(cfg.output, config.OutputConfig)
        assert isinstance(cfg.logging, config.LoggingConfig)

    def test_dockerfileai_config_custom_values(self):
        """Test DockerfileAIConfig with custom values."""
        cfg = config.DockerfileAIConfig(
            ollama=config.OllamaConfig(model="custom:7b"),
            output=config.OutputConfig(copy_mode=True),
        )
        assert cfg.ollama.model == "custom:7b"
        assert cfg.output.copy_mode is True


class TestGetConfigPath:
    """Tests for get_config_path function."""

    def test_get_config_path_returns_path(self):
        """Test that get_config_path returns a Path."""
        result = config.get_config_path()
        assert isinstance(result, Path)

    def test_get_config_path_in_home(self):
        """Test that config path is in home directory."""
        result = config.get_config_path()
        assert result.parent == Path.home()

    def test_get_config_path_filename(self):
        """Test that config path has correct filename."""
        result = config.get_config_path()
        assert result.name == ".dockerfileai.yaml"


class TestLoadConfigFile:
    """Tests for load_config_file function."""

    def test_load_nonexistent_file(self):
        """Test loading nonexistent config file."""
        result = config.load_config_file(Path("/nonexistent/.dockerfileai.yaml"))
        assert result == {}

    def test_load_valid_config_file(self, tmp_path):
        """Test loading valid config file."""
        config_file = tmp_path / ".dockerfileai.yaml"
        config_data = {
            "ollama": {"model": "custom:7b"},
            "output": {"copy_mode": True},
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        result = config.load_config_file(config_file)
        assert result["ollama"]["model"] == "custom:7b"
        assert result["output"]["copy_mode"] is True

    def test_load_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML file."""
        config_file = tmp_path / ".dockerfileai.yaml"
        with open(config_file, "w") as f:
            f.write("invalid: yaml: content:")

        with pytest.raises(ConfigurationError):
            config.load_config_file(config_file)

    def test_load_empty_yaml_file(self, tmp_path):
        """Test loading empty YAML file."""
        config_file = tmp_path / ".dockerfileai.yaml"
        config_file.write_text("")

        result = config.load_config_file(config_file)
        assert result == {}


class TestLoadEnvConfig:
    """Tests for load_env_config function."""

    def test_load_env_config_no_vars(self):
        """Test loading env config with no variables set."""
        # Clear environment
        env_vars = {
            "OLLAMA_HOST",
            "OLLAMA_PORT",
            "OLLAMA_MODEL",
            "OLLAMA_TIMEOUT",
            "DOCKERFILE_AI_SAVE_ANALYSIS",
            "DOCKERFILE_AI_LOG_LEVEL",
        }
        with patch.dict(os.environ, {}, clear=False):
            for var in env_vars:
                os.environ.pop(var, None)
            result = config.load_env_config()
            assert result == {}

    def test_load_env_config_ollama_vars(self):
        """Test loading env config with Ollama variables."""
        env = {
            "OLLAMA_HOST": "127.0.0.1",
            "OLLAMA_PORT": "8080",
            "OLLAMA_MODEL": "custom:7b",
        }
        with patch.dict(os.environ, env):
            result = config.load_env_config()
            assert result["ollama"]["host"] == "127.0.0.1"
            assert result["ollama"]["port"] == 8080
            assert result["ollama"]["model"] == "custom:7b"

    def test_load_env_config_output_vars(self):
        """Test loading env config with output variables."""
        env = {
            "DOCKERFILE_AI_COPY_MODE": "true",
            "DOCKERFILE_AI_OUTPUT_DIR": "/tmp/output",
        }
        with patch.dict(os.environ, env):
            result = config.load_env_config()
            assert result["output"]["copy_mode"] is True
            assert result["output"]["output_dir"] == "/tmp/output"

    def test_load_env_config_logging_vars(self):
        """Test loading env config with logging variables."""
        env = {
            "DOCKERFILE_AI_LOG_LEVEL": "DEBUG",
            "DOCKERFILE_AI_LOG_FILE": "/tmp/dockerfile_ai.log",
        }
        with patch.dict(os.environ, env):
            result = config.load_env_config()
            assert result["logging"]["level"] == "DEBUG"
            assert result["logging"]["log_file"] == "/tmp/dockerfile_ai.log"


class TestMergeConfigs:
    """Tests for merge_configs function."""

    def test_merge_single_config(self):
        """Test merging single config."""
        cfg = {"ollama": {"model": "custom:7b"}}
        result = config.merge_configs(cfg)
        assert result == cfg

    def test_merge_multiple_configs(self):
        """Test merging multiple configs."""
        cfg1 = {"ollama": {"model": "custom:7b"}}
        cfg2 = {"ollama": {"timeout": 60}, "logging": {"level": "DEBUG"}}
        result = config.merge_configs(cfg1, cfg2)

        assert result["ollama"]["model"] == "custom:7b"
        assert result["ollama"]["timeout"] == 60
        assert result["logging"]["level"] == "DEBUG"

    def test_merge_configs_override(self):
        """Test that later configs override earlier ones."""
        cfg1 = {"ollama": {"model": "model1:7b"}}
        cfg2 = {"ollama": {"model": "model2:7b"}}
        result = config.merge_configs(cfg1, cfg2)

        assert result["ollama"]["model"] == "model2:7b"

    def test_merge_empty_configs(self):
        """Test merging with empty configs."""
        result = config.merge_configs({}, {}, {})
        assert result == {}


class TestLoadConfiguration:
    """Tests for load_configuration function."""

    def test_load_configuration_defaults(self, monkeypatch):
        """Test load_configuration with defaults."""
        # Mock file loading to return empty
        monkeypatch.setattr(config, "load_config_file", lambda x: {})
        monkeypatch.setattr(config, "load_env_config", lambda: {})

        cfg = config.load_configuration()
        assert isinstance(cfg, config.DockerfileAIConfig)
        assert cfg.ollama.model == "qwen2.5-coder:7b"

    def test_load_configuration_with_override(self, monkeypatch):
        """Test load_configuration with override."""
        monkeypatch.setattr(config, "load_config_file", lambda x: {})
        monkeypatch.setattr(config, "load_env_config", lambda: {})

        override = {"ollama": {"model": "custom:7b"}}
        cfg = config.load_configuration(override=override)
        assert cfg.ollama.model == "custom:7b"

    def test_load_configuration_invalid(self, monkeypatch):
        """Test load_configuration with invalid config."""
        invalid_cfg = {"ollama": {"port": "not_a_number"}}
        monkeypatch.setattr(config, "load_config_file", lambda x: invalid_cfg)
        monkeypatch.setattr(config, "load_env_config", lambda: {})

        with pytest.raises(ConfigurationError):
            config.load_configuration()


class TestSaveConfig:
    """Tests for save_config function."""

    def test_save_config_default_path(self, tmp_path, monkeypatch):
        """Test saving config to default path."""
        config_path = tmp_path / ".dockerfileai.yaml"
        monkeypatch.setattr(config, "get_config_path", lambda: config_path)

        cfg = config.DockerfileAIConfig(
            ollama=config.OllamaConfig(model="custom:7b")
        )
        result = config.save_config(cfg)

        assert result == config_path
        assert config_path.exists()

    def test_save_config_custom_path(self, tmp_path):
        """Test saving config to custom path."""
        config_path = tmp_path / "custom.yaml"

        cfg = config.DockerfileAIConfig()
        result = config.save_config(cfg, config_path)

        assert result == config_path
        assert config_path.exists()

    def test_save_config_creates_directory(self, tmp_path):
        """Test that save_config creates necessary directories."""
        config_path = tmp_path / "subdir" / "subdir2" / "config.yaml"

        cfg = config.DockerfileAIConfig()
        config.save_config(cfg, config_path)

        assert config_path.exists()
        assert config_path.parent.exists()

    def test_save_config_valid_yaml(self, tmp_path):
        """Test that saved config is valid YAML."""
        config_path = tmp_path / "config.yaml"

        cfg = config.DockerfileAIConfig(
            ollama=config.OllamaConfig(model="custom:7b")
        )
        config.save_config(cfg, config_path)

        # Load and verify
        with open(config_path) as f:
            loaded = yaml.safe_load(f)

        assert loaded["ollama"]["model"] == "custom:7b"


class TestCreateSampleConfig:
    """Tests for create_sample_config function."""

    def test_create_sample_config_returns_string(self):
        """Test that create_sample_config returns a string."""
        result = config.create_sample_config()
        assert isinstance(result, str)

    def test_create_sample_config_is_valid_yaml(self):
        """Test that sample config is valid YAML."""
        sample = config.create_sample_config()
        loaded = yaml.safe_load(sample)

        assert "ollama" in loaded
        assert "output" in loaded
        assert "logging" in loaded

    def test_create_sample_config_contains_key_sections(self):
        """Test that sample config contains key sections."""
        sample = config.create_sample_config()

        assert "ollama:" in sample
        assert "output:" in sample
        assert "logging:" in sample
        assert "localhost" in sample
