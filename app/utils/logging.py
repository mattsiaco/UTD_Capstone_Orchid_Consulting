import json
import logging
import time
from typing import Any


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exc_info"] = self.formatException(record.exc_info)
        if hasattr(record, "extra"):
            log_obj.update(record.extra)
        return json.dumps(log_obj)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class LatencyTracker:
    def __init__(self, logger: logging.Logger, provider: str, operation: str):
        self._logger = logger
        self._provider = provider
        self._operation = operation
        self._start: float = 0.0

    def __enter__(self) -> "LatencyTracker":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        elapsed_ms = (time.perf_counter() - self._start) * 1000
        self._logger.info(
            "provider call finished",
            extra={
                "extra": {
                    "provider": self._provider,
                    "operation": self._operation,
                    "latency_ms": round(elapsed_ms, 2),
                    "success": exc_type is None,
                }
            },
        )
