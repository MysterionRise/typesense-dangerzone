"""Structured logging configuration using structlog."""

import logging
import sys
from typing import Any

import structlog


def setup_logging(
    level: int = logging.INFO,
    json_format: bool = False,
) -> None:
    """Configure structured logging for the application.

    Args:
        level: Logging level (default: INFO).
        json_format: If True, output JSON logs (for production).
                    If False, output human-readable logs (for development).
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    # Common processors for both formats
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_format:
        # Production: JSON output
        processors: list[structlog.types.Processor] = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Human-readable output
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__).

    Returns:
        A configured structlog logger.
    """
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger


def log_operation(
    logger: structlog.stdlib.BoundLogger,
    operation: str,
    **kwargs: Any,
) -> None:
    """Log an operation with structured context.

    Args:
        logger: The logger instance to use.
        operation: Name of the operation being performed.
        **kwargs: Additional context to include in the log.
    """
    logger.info("operation_started", operation=operation, **kwargs)
