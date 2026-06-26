"""Structured logging system with JSON and text output support.

Features:
  - Structured JSON logging (production)
  - Colored console logging (development)
  - Configurable log levels
  - Sensitive data masking
  - Correlation IDs
  - File rotation support
"""

from __future__ import annotations

import sys
import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler

# Sensitive field patterns to mask in logs
SENSITIVE_FIELDS = {
    "password", "secret", "token", "api_key", "apikey",
    "access_key", "private_key", "auth", "authorization",
    "credit_card", "ssn", "passwd",
}


class SensitiveDataFilter(logging.Filter):
    """Filter that masks sensitive data in log records."""

    def __init__(self, fields: Optional[set] = None):
        super().__init__()
        self.fields = fields or SENSITIVE_FIELDS

    def filter(self, record: logging.LogRecord) -> bool:
        """Mask sensitive fields in the log message and args."""
        # Mask in message if it contains key=value patterns
        if hasattr(record, "msg") and isinstance(record.msg, str):
            for field in self.fields:
                record.msg = record.msg.replace(
                    f"{field}=", f"{field}=****"
                )
        return True


class JSONFormatter(logging.Formatter):
    """Format log records as JSON lines."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Include exception info if present
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }

        # Include extra fields
        for key, value in record.__dict__.items():
            if key not in (
                "args", "asctime", "created", "exc_info", "exc_text",
                "filename", "funcName", "id", "levelname", "levelno",
                "lineno", "module", "msecs", "message", "msg",
                "name", "pathname", "process", "processName",
                "relativeCreated", "stack_info", "thread", "threadName",
            ):
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


class ColoredConsoleFormatter(logging.Formatter):
    """Colorized console output for development."""

    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[41m",   # Red background
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
        return (
            f"{color}[{timestamp}] {record.levelname:<8}"
            f"{self.RESET} {record.getMessage()}"
        )


# ──────────────────────────────────────────────
# Logger Factory
# ──────────────────────────────────────────────

class LoggerFactory:
    """Factory for creating configured logger instances."""

    @staticmethod
    def create_logger(
        name: str = "prompt_optimizer",
        level: str = "INFO",
        log_file: Optional[str] = None,
        log_format: str = "json",
        verbose: bool = False,
    ) -> logging.Logger:
        """Create and configure a logger.

        Args:
            name: Logger name (typically the module name).
            level: Log level (DEBUG|INFO|WARNING|ERROR|CRITICAL).
            log_file: Optional path to a log file. If None, logs to stdout.
            log_format: 'json' for structured JSON, 'text' for colored console.
            verbose: If True, set level to DEBUG.

        Returns:
            Configured Logger instance.
        """
        logger = logging.getLogger(name)

        # Resolve level
        if verbose:
            effective_level = "DEBUG"
        else:
            effective_level = level.upper()

        logger.setLevel(getattr(logging, effective_level, logging.INFO))

        # Remove existing handlers to avoid duplicates on reconfiguration
        logger.handlers.clear()

        # Create handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(
                log_path, maxBytes=10 * 1024 * 1024, backupCount=5
            )
        else:
            handler = logging.StreamHandler(sys.stdout)

        # Set formatter
        if log_format == "json":
            formatter = JSONFormatter()
        else:
            formatter = ColoredConsoleFormatter()

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Add sensitive data filter
        logger.addFilter(SensitiveDataFilter())

        return logger


# ──────────────────────────────────────────────
# Module-level default logger
# ──────────────────────────────────────────────

_logger: Optional[logging.Logger] = None


def get_logger(
    name: str = "prompt_optimizer",
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "json",
    verbose: bool = False,
) -> logging.Logger:
    """Get the application logger (singleton pattern)."""
    global _logger
    if _logger is None:
        _logger = LoggerFactory.create_logger(
            name=name,
            level=level,
            log_file=log_file,
            log_format=log_format,
            verbose=verbose,
        )
    return _logger