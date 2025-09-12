# core/logging/logger_config.py

import logging, warnings
import sys
from config import LogConfig  # sigues usando tu config en raíz

# Redirige las advertencias del módulo 'warnings' al sistema de logging
logging.captureWarnings(True)

def setup_logging(log_level: str | None = None):
    """
    Idempotente: llama varias veces sin duplicar handlers.
    - Si log_level se pasa, tiene prioridad (CLI / FastAPI).
    - Si no, usa LogConfig.LOG_LEVEL (servicio).
    """
    level_str = (log_level or getattr(LogConfig, "LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_str, logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # Si ya hay handlers, solo ajustamos el nivel y salimos (no duplicar handlers)
    if root.handlers:
        return root

    fmt = getattr(LogConfig, "LOG_FORMAT", "%(asctime)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter(fmt)

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    fh = logging.FileHandler(getattr(LogConfig, "LOG_FILE", "app.log"), mode="a", encoding="utf-8")
    fh.setFormatter(formatter)
    root.addHandler(fh)

    return root

def get_logger(name: str):
    return logging.getLogger(name)
