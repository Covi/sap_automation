# utils/logger.py
# Módulo de configuración del logger para el proyecto SAP Automation

import logging
import sys
from config import LogConfig # <-- Importamos la configuración

# Leemos la configuración de LogConfig, con valores por defecto por si acaso
logger_name = getattr(LogConfig, 'LOGGER_NAME', 'default_logger')
log_level_str = getattr(LogConfig, 'LOG_LEVEL', 'INFO').upper()
log_file = getattr(LogConfig, 'LOG_FILE', 'default.log')
log_format = getattr(LogConfig, 'LOG_FORMAT', '%(asctime)s - %(message)s')

# Convertimos el nivel de log de string a la constante de logging (ej. "INFO" -> 10)
log_level = getattr(logging, log_level_str, logging.INFO)

# --- El resto del código es casi igual ---
log = logging.getLogger(logger_name)
log.setLevel(log_level)

formatter = logging.Formatter(log_format)

if not log.handlers:
    # Handler para la consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    # Handler para el fichero
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)