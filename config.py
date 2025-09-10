import os
from dotenv import load_dotenv
from dataclasses import dataclass, field
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any

# --- Carga de entorno ---
load_dotenv()

# --- Configuración General ---
SAP_BASE_URL = os.getenv("SAP_URL", "https://s4pf.refrival.com/sap/bc/gui/sap/its/webgui?sap-language=ES")
DEFAULT_TIMEOUT = 30000
DEFAULT_BROWSER = os.getenv("BROWSER", "firefox")

# --- Definición de Rutas del Proyecto ---
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

# --- 1. Se crea una clase base abstracta con el contrato ---
@dataclass(frozen=True)
class BaseConfig(ABC):
    """
    Configuración base inmutable con atributos compartidos y un contrato
    para obtener los valores por defecto.
    """
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
    
    DOWNLOAD_DIR: str = os.getenv("DOWNLOAD_DIR", "/home/covi/Descargas")

    @abstractmethod
    def get_default_data(self) -> Dict[str, Any]:
        """
        Contrato que obliga a las subclases a definir explícitamente
        sus valores por defecto para el modelo de datos.
        """
        pass

# --- 2. Las clases específicas ahora heredan e implementan el contrato ---
@dataclass(frozen=True)
class Mb52Config(BaseConfig):
    """Configuración específica para MB52."""
    TRANSACTION_CODE: str = "MB52"
    EXPORT_FILENAME: str = "STOCK.xlsx"
    LOCATOR_FILE: str = "mb52.toml"
    DEFAULT_CENTRO: str = "E086"

    def get_default_data(self) -> Dict[str, Any]:
        return {
            "centro": self.DEFAULT_CENTRO
        }

@dataclass(frozen=True)
class Iq09Config(BaseConfig):
    """Configuración específica para IQ09."""
    TRANSACTION_CODE: str = "IQ09"
    EXPORT_FILENAME: str = "STOCK_SERIADO.xlsx"
    LOCATOR_FILE: str = "iq09.toml"
    DEFAULT_CENTRO: str = "E086"

    def get_default_data(self) -> Dict[str, Any]:
        # Esta transacción no tiene defaults, devuelve un dict vacío.
        return {}

@dataclass(frozen=True)
class ZsinOrdenesConfig(BaseConfig):
    """Configuración para la transacción ZSIN_ORDENES."""
    TRANSACTION_CODE: str = "ZSIN_ORDENES"
    DOWNLOAD_DIR: str = "/home/covi/Descargas/ordenes_sap"
    EXPORT_FILENAME: str = "smart"
    LOCATOR_FILE: str = "zsin_ordenes.toml"
    DEFAULT_STATUS: str = "SE"
    DEFAULT_CLASE: str = "ZR04,ZR05"
    DEFAULT_CENTRO: str = "E086"

    def get_default_data(self) -> Dict[str, Any]:
        return {
            "status": self.DEFAULT_STATUS,
            "clase": self.DEFAULT_CLASE
        }