"""Tests for the prompts module."""
import pytest
from pathlib import Path
from dockerfile_ai import prompts


class TestGetPromptPath:
    """Tests for get_prompt_path function."""

    def test_get_prompt_path_returns_path(self):
        """Test that get_prompt_path returns a Path object."""
        result = prompts.get_prompt_path()
        assert isinstance(result, Path)

    def test_get_prompt_path_contains_prompts_dir(self):
        """Test that the path contains 'prompts' directory."""
        result = prompts.get_prompt_path()
        assert "prompts" in str(result)

    def test_get_prompt_path_exists(self):
        """Test that the prompts path exists."""
        result = prompts.get_prompt_path()
        assert result.exists()


class TestReadPrompt:
    """Tests for read_prompt function."""

    def test_read_prompt_v2_default(self):
        """Test reading the default v2 prompt."""
        result = prompts.read_prompt()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_read_prompt_v2_explicit(self):
        """Test reading v2 prompt explicitly."""
        result = prompts.read_prompt("v2")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_read_prompt_v1(self):
        """Test reading v1 prompt."""
        result = prompts.read_prompt("v1")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_read_prompt_nonexistent(self):
        """Test that nonexistent prompt raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            prompts.read_prompt("v999")

    def test_read_prompt_returns_string(self):
        """Test that read_prompt returns a string."""
        result = prompts.read_prompt()
        assert isinstance(result, str)


class TestFormatPrompt:
    """Tests for format_prompt function."""

    def test_format_prompt_with_dockerfile_content(self, sample_dockerfile):
        """Test formatting a prompt with Dockerfile content."""
        result = prompts.format_prompt(sample_dockerfile)
        assert isinstance(result, str)
        assert sample_dockerfile in result
        assert "FROM python:3.9-slim" in result

    def test_format_prompt_uses_default_template(self, sample_dockerfile):
        """Test that format_prompt uses default template when none provided."""
        result = prompts.format_prompt(sample_dockerfile)
        # Should contain both the template and the Dockerfile content
        assert len(result) > len(sample_dockerfile)

    def test_format_prompt_with_custom_template(self, sample_dockerfile):
        """Test format_prompt with custom template."""
        custom_template = "Analyze this: {}"
        # Note: current implementation doesn't use {} placeholder,
        # it just concatenates. Test what it actually does.
        result = prompts.format_prompt(sample_dockerfile, custom_template)
        assert custom_template in result
        assert sample_dockerfile in result

    def test_format_prompt_none_dockerfile_content(self):
        """Test formatting with empty Dockerfile content."""
        result = prompts.format_prompt("")
        assert isinstance(result, str)

    def test_format_prompt_concatenates_correctly(self, sample_dockerfile):
        """Test that format_prompt properly concatenates template and content."""
        result = prompts.format_prompt(sample_dockerfile)
        assert sample_dockerfile in result
        # Should have newlines between template and content
        assert "\n\n" in result


class TestPromptIntegration:
    """Integration tests for prompt functionality."""

    def test_read_and_format_prompt_flow(self, sample_dockerfile):
        """Test complete flow of reading and formatting a prompt."""
        prompt_template = prompts.read_prompt("v2")
        formatted = prompts.format_prompt(sample_dockerfile, prompt_template)

        assert isinstance(formatted, str)
        assert len(formatted) > 0
        assert sample_dockerfile in formatted
        assert prompt_template in formatted

    def test_default_prompt_is_readable(self):
        """Test that the default prompt is readable and non-empty."""
        default_prompt = prompts.read_prompt()
        assert len(default_prompt) > 100  # Should be a substantial prompt
