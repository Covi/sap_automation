# Fichero: config.py

import os
from dotenv import load_dotenv
from dataclasses import dataclass, field
from pathlib import Path

# --- Carga de entorno ---
load_dotenv()

# --- Configuración General ---
BASE_URL = os.getenv("SAP_URL", "https://s4pf.refrival.com/sap/bc/gui/sap/its/webgui?sap-language=ES")
DEFAULT_TIMEOUT = 30000
DEFAULT_BROWSER = os.getenv("BROWSER", "firefox")

# --- Definición de Rutas del Proyecto ---
# Se define la raíz del proyecto y directorios clave para tener una única fuente de verdad.
PROJECT_ROOT = Path(__file__).resolve().parent
LOCATORS_DIR = PROJECT_ROOT / "locators"

# Rutas a ficheros de localizadores comunes
COMMON_LOCATORS_PATH = LOCATORS_DIR / "common.toml"
LOGIN_LOCATORS_PATH = LOCATORS_DIR / "login.toml"
EASY_ACCESS_LOCATORS_PATH = LOCATORS_DIR / "easy_access.toml"


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
    # CAMBIO: Se usa field para añadir metadatos y ocultar las credenciales
    SAP_USERNAME: str = field(
        default=os.getenv("SAP_USER"), 
        metadata={'sensitive': True}, 
        repr=False
    )
    SAP_PASSWORD: str = field(
        default=os.getenv("SAP_PASSWORD"), 
        metadata={'sensitive': True}, 
        repr=False
    )
    
    # El resto de los campos permanece igual
    DOWNLOAD_DIR: str = os.getenv("DOWNLOAD_DIR", "/home/covi/Descargas")
    DEFAULT_CENTRO: str = "E086"  # Valor por defecto común, puede ser sobrescrito

# --- 2. Las clases específicas ahora heredan de BaseConfig ---
@dataclass(frozen=True)
class Mb52Config(BaseConfig):
    """Configuración específica para MB52. Hereda usuario, pass y dir de descarga."""
    TRANSACTION_CODE: str = "MB52"
    EXPORT_FILENAME: str = "STOCK.xlsx"
    # CAMBIO: Ahora solo contiene el nombre del fichero. La ruta completa se construirá en la factory.
    LOCATOR_FILE: str = "mb52.toml"

@dataclass(frozen=True)
class Iq09Config(BaseConfig):
    """Configuración específica para IQ09. Hereda usuario, pass y dir de descarga."""
    TRANSACTION_CODE: str = "IQ09"
    EXPORT_FILENAME: str = "STOCK_SERIADO.xlsx"
    # CAMBIO: Ahora solo contiene el nombre del fichero.
    LOCATOR_FILE: str = "iq09.toml"

@dataclass(frozen=True)
class ZsinOrdenesConfig(BaseConfig):
    """Configuración para la nueva transacción ZSIN_ORDENES."""
    TRANSACTION_CODE: str = "ZSIN_ORDENES"
    DOWNLOAD_DIR: str = "/home/covi/Descargas/ordenes_sap"
    EXPORT_FILENAME: str = "smart"
    # CAMBIO: Ahora solo contiene el nombre del fichero.
    LOCATOR_FILE: str = "zsin_ordenes.toml"