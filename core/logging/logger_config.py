# core/logging/logger_config.py

import logging, warnings
import sys

# TODO: [REFACTOR] Desacoplar. Injectar configuración en lugar de importar settings globales.
from config import settings 

# Redirige las advertencias del módulo 'warnings' al sistema de logging
logging.captureWarnings(True)

def setup_logging(log_level: str | None = None):
    """
    Idempotente: llama varias veces sin duplicar handlers.
    - Si log_level se pasa, tiene prioridad (CLI / FastAPI).
    - Si no, usa settings.logging.log_level.
    """
    # 1. Determinamos el nivel
    #    Prioridad: Argumento explícito > Configuración TOML > Default 'INFO'
    config_level = settings.logging.log_level
    level_str = (log_level or config_level).upper()
    
    level = getattr(logging, level_str, logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # Si ya hay handlers, solo ajustamos el nivel y salimos (no duplicar handlers)
    if root.handlers:
        return root

    # 2. Configuración del Formato
    fmt = settings.logging.log_format
    formatter = logging.Formatter(fmt)

    # 3. Handler de Consola
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # 4. Handler de Archivo
    fh = logging.FileHandler(settings.logging.log_file, mode="a", encoding="utf-8")
    fh.setFormatter(formatter)
    root.addHandler(fh)

    return root

def get_logger(name: str):
    return logging.getLogger(name)