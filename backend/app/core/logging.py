import logging
import sys
import json
from datetime import datetime, timezone


class StructuredJsonFormatter(logging.Formatter):
    """Custom formatter that outputs JSON logs with timestamps and redactions."""

    SENSITIVE_KEYS = {"api_key", "secret", "password", "token", "service_role", "authorization"}

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "request_id"):
            log_obj["request_id"] = getattr(record, "request_id")
        if hasattr(record, "conversation_id"):
            log_obj["conversation_id"] = getattr(record, "conversation_id")
        if hasattr(record, "extra_data"):
            extra = getattr(record, "extra_data")
            if isinstance(extra, dict):
                # Sanitize sensitive fields
                sanitized = {}
                for k, v in extra.items():
                    if any(s in k.lower() for s in self.SENSITIVE_KEYS):
                        sanitized[k] = "[REDACTED]"
                    else:
                        sanitized[k] = v
                log_obj["data"] = sanitized

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logger(name: str = "ems_chatbot") -> logging.Logger:
    """Set up structured logger for the application."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)

    return logger


logger = setup_logger()
