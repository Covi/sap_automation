# Fichero: config.py

import os
from dotenv import load_dotenv
from dataclasses import dataclass

# --- Carga de entorno ---
load_dotenv()

# --- Configuración General ---
SAP_BASE_URL = os.getenv("SAP_URL", "https://s4pf.refrival.com/sap/bc/gui/sap/its/webgui?sap-language=ES")
DEFAULT_TIMEOUT = 30000
DEFAULT_BROWSER = os.getenv("BROWSER", "firefox")

# --- Configuración del Logger ---
@dataclass(frozen=True)
class LogConfig:
    """Configuración inmutable para el logger."""
    LOGGER_NAME: str = "sap_automation"
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "automation.log"
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

# --- 1. Se crea una clase base con los atributos comunes ---
@dataclass(frozen=True)
class BaseConfig:
    """
    Configuración base inmutable con atributos compartidos por todas las transacciones.
    'frozen=True' evita que estos valores se puedan modificar por error durante la ejecución.
    """
    SAP_USERNAME: str = os.getenv("SAP_USER")
    SAP_PASSWORD: str = os.getenv("SAP_PASSWORD")
    DOWNLOAD_DIR: str = os.getenv("DOWNLOAD_DIR", "/home/covi/Descargas")
    DEFAULT_CENTRO: str = "E086"  # Valor por defecto común, puede ser sobrescrito

# --- 2. Las clases específicas ahora heredan de BaseConfig ---
@dataclass(frozen=True)
class Mb52Config(BaseConfig):
    """Configuración específica para MB52. Hereda usuario, pass y dir de descarga."""
    TRANSACTION_CODE: str = "MB52"
    EXPORT_FILENAME: str = "STOCK.xlsx"
    LOCATOR_FILE: str = "locators/mb52.toml"

@dataclass(frozen=True)
class Iq09Config(BaseConfig):
    """Configuración específica para IQ09. Hereda usuario, pass y dir de descarga."""
    TRANSACTION_CODE: str = "IQ09"
    EXPORT_FILENAME: str = "STOCK_SERIADO.xlsx"
    LOCATOR_FILE: str = "locators/iq09.toml"

@dataclass(frozen=True)
class ZsinOrdenesConfig(BaseConfig):
    """Configuración para la nueva transacción ZSIN_ORDENES."""
    TRANSACTION_CODE: str = "ZSIN_ORDENES"
    LOCATOR_FILE: str = "locators/zsin_ordenes.toml"
    DOWNLOAD_DIR: str = "/home/covi/Descargas/ordenes_sap"
    EXPORT_FILENAME: str = "smart"