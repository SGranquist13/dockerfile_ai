"""Resilience patterns for dockerfile_ai - retry logic, timeouts, and connection validation."""
import asyncio
import time
from typing import Callable, Any, Optional, TypeVar, Coroutine
import httpx

from .exceptions import OllamaConnectionError
from .logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry logic."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 32.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number.

        Args:
            attempt: Zero-based attempt number

        Returns:
            Delay in seconds
        """
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt), self.max_delay
        )

        if self.jitter:
            import random

            delay = delay * (0.5 + random.random())

        return delay


async def retry_async(
    func: Callable[..., Coroutine[Any, Any, T]],
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs,
) -> T:
    """Execute an async function with exponential backoff retry.

    Args:
        func: Async function to call
        *args: Positional arguments for func
        config: RetryConfig instance
        **kwargs: Keyword arguments for func

    Returns:
        Return value from func

    Raises:
        Exception: Original exception after max retries exceeded
    """
    if config is None:
        config = RetryConfig()

    last_exception = None

    for attempt in range(config.max_retries + 1):
        try:
            logger.debug(
                f"Executing {func.__name__} (attempt {attempt + 1}/{config.max_retries + 1})"
            )
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            if attempt < config.max_retries:
                delay = config.get_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}. "
                    f"Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"All {config.max_retries + 1} attempts failed for {func.__name__}"
                )

    raise last_exception


def retry_sync(
    func: Callable[..., T],
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs,
) -> T:
    """Execute a sync function with exponential backoff retry.

    Args:
        func: Function to call
        *args: Positional arguments for func
        config: RetryConfig instance
        **kwargs: Keyword arguments for func

    Returns:
        Return value from func

    Raises:
        Exception: Original exception after max retries exceeded
    """
    if config is None:
        config = RetryConfig()

    last_exception = None

    for attempt in range(config.max_retries + 1):
        try:
            logger.debug(
                f"Executing {func.__name__} (attempt {attempt + 1}/{config.max_retries + 1})"
            )
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            if attempt < config.max_retries:
                delay = config.get_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}. "
                    f"Retrying in {delay:.2f}s..."
                )
                time.sleep(delay)
            else:
                logger.error(
                    f"All {config.max_retries + 1} attempts failed for {func.__name__}"
                )

    raise last_exception


async def validate_ollama_connection(
    host: str = "localhost",
    port: int = 11434,
    timeout: int = 5,
) -> bool:
    """Validate connection to Ollama service.

    Args:
        host: Ollama host
        port: Ollama port
        timeout: Connection timeout in seconds

    Returns:
        True if connection is valid

    Raises:
        OllamaConnectionError: If connection cannot be established
    """
    url = f"http://{host}:{port}/api/tags"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()
            logger.debug(f"Successfully connected to Ollama at {host}:{port}")
            return True
    except httpx.ConnectError as e:
        raise OllamaConnectionError(
            f"Cannot connect to Ollama at {host}:{port}. "
            f"Is Ollama running? Error: {str(e)}"
        )
    except httpx.TimeoutException as e:
        raise OllamaConnectionError(
            f"Connection to Ollama at {host}:{port} timed out. Error: {str(e)}"
        )
    except httpx.HTTPError as e:
        raise OllamaConnectionError(
            f"HTTP error connecting to Ollama: {str(e)}"
        )
    except Exception as e:
        raise OllamaConnectionError(
            f"Unexpected error validating Ollama connection: {str(e)}"
        )


async def check_model_available(
    model: str,
    host: str = "localhost",
    port: int = 11434,
    timeout: int = 5,
) -> bool:
    """Check if a model is available in Ollama.

    Args:
        model: Model name to check
        host: Ollama host
        port: Ollama port
        timeout: Connection timeout in seconds

    Returns:
        True if model is available

    Raises:
        OllamaConnectionError: If connection fails
    """
    url = f"http://{host}:{port}/api/tags"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()
            data = response.json()

            models = [m.get("name", "") for m in data.get("models", [])]
            available = any(model in m for m in models)

            if available:
                logger.debug(f"Model {model} is available in Ollama")
            else:
                logger.warning(
                    f"Model {model} not found in Ollama. "
                    f"Available models: {', '.join(models)}"
                )

            return available
    except httpx.HTTPError as e:
        raise OllamaConnectionError(
            f"Error checking model availability: {str(e)}"
        )
    except Exception as e:
        raise OllamaConnectionError(
            f"Unexpected error checking model: {str(e)}"
        )


class CircuitBreaker:
    """Circuit breaker pattern for handling failing services."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        name: str = "default",
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before breaking
            recovery_timeout: Seconds to wait before trying to recover
            name: Name for logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False

    def record_success(self):
        """Record a successful operation."""
        self.failure_count = 0
        self.is_open = False
        logger.debug(f"Circuit breaker {self.name}: Success recorded")

    def record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning(
                f"Circuit breaker {self.name}: Opened after "
                f"{self.failure_count} failures"
            )

    def should_attempt(self) -> bool:
        """Check if operation should be attempted.

        Returns:
            True if operation should be attempted
        """
        if not self.is_open:
            return True

        # Check if recovery timeout has passed
        if self.last_failure_time is None:
            return True

        elapsed = time.time() - self.last_failure_time
        if elapsed > self.recovery_timeout:
            logger.info(f"Circuit breaker {self.name}: Attempting recovery")
            self.is_open = False
            self.failure_count = 0
            return True

        return False

    async def call_async(
        self,
        func: Callable[..., Coroutine[Any, Any, T]],
        *args,
        **kwargs,
    ) -> T:
        """Execute an async function with circuit breaker protection.

        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Return value from func

        Raises:
            OllamaConnectionError: If circuit is open
        """
        if not self.should_attempt():
            raise OllamaConnectionError(
                f"Circuit breaker {self.name} is open. "
                f"Service appears to be unavailable."
            )

        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise
