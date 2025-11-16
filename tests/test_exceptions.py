"""Tests for the exceptions module."""
import pytest
from dockerfile_ai import exceptions


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_base_exception_inherits_from_exception(self):
        """Test that DockerfileAIException inherits from Exception."""
        assert issubclass(exceptions.DockerfileAIException, Exception)

    def test_specific_exceptions_inherit_from_base(self):
        """Test that specific exceptions inherit from base."""
        assert issubclass(exceptions.DockerfileError, exceptions.DockerfileAIException)
        assert issubclass(exceptions.OllamaConnectionError, exceptions.DockerfileAIException)
        assert issubclass(exceptions.OllamaError, exceptions.DockerfileAIException)
        assert issubclass(exceptions.ConfigurationError, exceptions.DockerfileAIException)
        assert issubclass(exceptions.OutputError, exceptions.DockerfileAIException)
        assert issubclass(exceptions.ValidationError, exceptions.DockerfileAIException)

    def test_ollama_response_error_inherits_from_ollama_error(self):
        """Test that OllamaResponseError inherits from OllamaError."""
        assert issubclass(exceptions.OllamaResponseError, exceptions.OllamaError)


class TestExceptionRaising:
    """Tests for raising and catching exceptions."""

    def test_raise_dockerfile_error(self):
        """Test raising DockerfileError."""
        with pytest.raises(exceptions.DockerfileError):
            raise exceptions.DockerfileError("Test error")

    def test_raise_ollama_connection_error(self):
        """Test raising OllamaConnectionError."""
        with pytest.raises(exceptions.OllamaConnectionError):
            raise exceptions.OllamaConnectionError("Connection failed")

    def test_raise_ollama_error(self):
        """Test raising OllamaError."""
        with pytest.raises(exceptions.OllamaError):
            raise exceptions.OllamaError("Ollama error")

    def test_raise_ollama_response_error(self):
        """Test raising OllamaResponseError."""
        with pytest.raises(exceptions.OllamaResponseError):
            raise exceptions.OllamaResponseError("Bad response")

    def test_raise_configuration_error(self):
        """Test raising ConfigurationError."""
        with pytest.raises(exceptions.ConfigurationError):
            raise exceptions.ConfigurationError("Bad config")

    def test_raise_output_error(self):
        """Test raising OutputError."""
        with pytest.raises(exceptions.OutputError):
            raise exceptions.OutputError("Output failed")

    def test_raise_validation_error(self):
        """Test raising ValidationError."""
        with pytest.raises(exceptions.ValidationError):
            raise exceptions.ValidationError("Invalid input")


class TestExceptionCatching:
    """Tests for catching exceptions with hierarchy."""

    def test_catch_base_exception(self):
        """Test catching base DockerfileAIException."""
        try:
            raise exceptions.DockerfileError("Test error")
        except exceptions.DockerfileAIException as e:
            assert str(e) == "Test error"

    def test_catch_specific_exception(self):
        """Test catching specific exception type."""
        try:
            raise exceptions.OllamaResponseError("Bad response")
        except exceptions.OllamaResponseError as e:
            assert str(e) == "Bad response"

    def test_ollama_response_error_caught_as_ollama_error(self):
        """Test that OllamaResponseError can be caught as OllamaError."""
        try:
            raise exceptions.OllamaResponseError("Bad response")
        except exceptions.OllamaError as e:
            assert "Bad response" in str(e)

    def test_all_exceptions_caught_as_base(self):
        """Test that all exceptions can be caught as DockerfileAIException."""
        exceptions_to_test = [
            exceptions.DockerfileError("test"),
            exceptions.OllamaConnectionError("test"),
            exceptions.OllamaError("test"),
            exceptions.OllamaResponseError("test"),
            exceptions.ConfigurationError("test"),
            exceptions.OutputError("test"),
            exceptions.ValidationError("test"),
        ]

        for exc in exceptions_to_test:
            with pytest.raises(exceptions.DockerfileAIException):
                raise exc


class TestExceptionMessages:
    """Tests for exception messages."""

    def test_exception_with_message(self):
        """Test exception with custom message."""
        msg = "Custom error message"
        exc = exceptions.DockerfileError(msg)
        assert str(exc) == msg

    def test_exception_without_message(self):
        """Test exception without message."""
        exc = exceptions.OllamaError()
        assert isinstance(exc, exceptions.OllamaError)

    def test_multiple_exception_arguments(self):
        """Test exception with multiple arguments."""
        exc = exceptions.ValidationError("Field", "invalid value")
        assert "Field" in str(exc)
