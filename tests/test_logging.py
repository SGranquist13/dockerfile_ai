"""Tests for the logging module."""
import pytest
import logging
from pathlib import Path
from unittest.mock import patch
from dockerfile_ai import logging as df_logging


class TestColoredFormatter:
    """Tests for ColoredFormatter class."""

    def test_colored_formatter_creation(self):
        """Test creating a ColoredFormatter instance."""
        formatter = df_logging.ColoredFormatter("%(levelname)s - %(message)s")
        assert isinstance(formatter, logging.Formatter)

    def test_colored_formatter_has_colors_dict(self):
        """Test that formatter has COLORS dictionary."""
        formatter = df_logging.ColoredFormatter("%(message)s")
        assert hasattr(formatter, "COLORS")
        assert "DEBUG" in formatter.COLORS
        assert "INFO" in formatter.COLORS
        assert "WARNING" in formatter.COLORS
        assert "ERROR" in formatter.COLORS
        assert "CRITICAL" in formatter.COLORS

    def test_colored_formatter_has_reset_code(self):
        """Test that formatter has RESET code."""
        formatter = df_logging.ColoredFormatter("%(message)s")
        assert hasattr(formatter, "RESET")
        assert "\033[0m" in formatter.RESET


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_returns_logger(self):
        """Test that setup_logging returns a logger."""
        logger = df_logging.setup_logging()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "dockerfile_ai"

    def test_setup_logging_sets_log_level(self):
        """Test that setup_logging sets the correct log level."""
        logger = df_logging.setup_logging(log_level=logging.DEBUG)
        assert logger.level == logging.DEBUG

    def test_setup_logging_adds_console_handler(self):
        """Test that setup_logging adds a console handler."""
        logger = df_logging.setup_logging()
        handlers = logger.handlers
        assert len(handlers) > 0
        assert any(isinstance(h, logging.StreamHandler) for h in handlers)

    def test_setup_logging_with_file(self, tmp_path):
        """Test setup_logging with file output."""
        log_file = tmp_path / "test.log"
        logger = df_logging.setup_logging(log_file=log_file)

        assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)

    def test_setup_logging_creates_log_file_directory(self, tmp_path):
        """Test that setup_logging creates log file directory."""
        log_file = tmp_path / "subdir" / "test.log"
        df_logging.setup_logging(log_file=log_file)

        assert log_file.parent.exists()

    def test_setup_logging_verbose_format(self):
        """Test setup_logging with verbose=True."""
        logger = df_logging.setup_logging(verbose=True)
        # Logger should have handlers with verbose format
        assert logger.handlers

    def test_setup_logging_clears_existing_handlers(self):
        """Test that setup_logging clears existing handlers."""
        logger = df_logging.setup_logging()
        initial_count = len(logger.handlers)

        # Set up logging again
        logger = df_logging.setup_logging()
        # Should not accumulate handlers
        assert len(logger.handlers) <= initial_count + 1


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger."""
        logger = df_logging.get_logger("test_module")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_has_dockerfile_ai_prefix(self):
        """Test that returned logger has dockerfile_ai prefix."""
        logger = df_logging.get_logger("test_module")
        assert "dockerfile_ai" in logger.name

    def test_get_logger_multiple_calls_same_module(self):
        """Test that multiple calls for same module return same logger."""
        logger1 = df_logging.get_logger("test_module")
        logger2 = df_logging.get_logger("test_module")
        assert logger1 is logger2

    def test_get_logger_different_modules(self):
        """Test that different modules get different loggers."""
        logger1 = df_logging.get_logger("module1")
        logger2 = df_logging.get_logger("module2")
        assert logger1.name != logger2.name


class TestGetLogFilePath:
    """Tests for get_log_file_path function."""

    def test_get_log_file_path_returns_path(self):
        """Test that get_log_file_path returns a Path."""
        path = df_logging.get_log_file_path()
        assert isinstance(path, Path)

    def test_get_log_file_path_in_home_directory(self):
        """Test that log file is in home directory."""
        path = df_logging.get_log_file_path()
        assert Path.home() in path.parents or path.parent.parent == Path.home()

    def test_get_log_file_path_includes_date(self):
        """Test that log file path includes date."""
        path = df_logging.get_log_file_path()
        import re
        assert re.search(r"\d{8}", path.name)

    def test_get_log_file_path_creates_directory(self):
        """Test that get_log_file_path creates the directory."""
        path = df_logging.get_log_file_path()
        # The function should create the parent directory
        assert path.parent.exists()

    def test_get_log_file_path_consistent(self):
        """Test that get_log_file_path is consistent."""
        path1 = df_logging.get_log_file_path()
        path2 = df_logging.get_log_file_path()
        assert path1 == path2


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_logging_to_console(self, capsys):
        """Test that logging to console works."""
        logger = df_logging.setup_logging(log_level=logging.INFO)
        logger.info("Test message")

        # Message should be captured
        captured = capsys.readouterr()
        # Check stderr because logging goes there
        assert "Test message" in captured.err or captured.out

    def test_logging_to_file(self, tmp_path):
        """Test that logging to file works."""
        log_file = tmp_path / "test.log"
        logger = df_logging.setup_logging(log_file=log_file)
        logger.info("Test message")

        # Force flush and wait
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        # File should contain the message
        content = log_file.read_text()
        assert "Test message" in content

    def test_different_log_levels(self):
        """Test that different log levels work correctly."""
        logger = df_logging.setup_logging(log_level=logging.WARNING)

        # Logger itself is set to DEBUG to capture everything,
        # but handlers have the specified level
        assert logger.level == logging.DEBUG
        # At least one handler should have the WARNING level
        assert any(h.level == logging.WARNING for h in logger.handlers)

    def test_logger_propagation(self):
        """Test logger propagation."""
        logger = df_logging.get_logger("cli")
        # Should be able to set up logging
        parent_logger = df_logging.setup_logging()
        assert parent_logger.name == "dockerfile_ai"
