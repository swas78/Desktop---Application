# For: Structured JSON logging with automated PII masking
# Must never: Output raw applicant personal values or unmasked secrets

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

SENSITIVE_KEYS = {
    "password", "password_hash", "access_token", "refresh_token",
    "jwt_secret", "launch_token", "full_name", "father_name",
    "dob", "roll_no", "reg_no", "aadhaar", "marks"
}


def mask_sensitive_data(data: Any) -> Any:
    """Mask sensitive fields recursively to prevent PII leakage in logs."""
    if isinstance(data, dict):
        return {
            k: "***MASKED***" if k.lower() in SENSITIVE_KEYS else mask_sensitive_data(v)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    return data


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_payload["context"] = mask_sensitive_data(record.extra)
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_payload)


def get_logger(name: str) -> logging.Logger:
    """Configures and returns a structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
