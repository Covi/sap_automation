# Fichero: config.py

import os
from dotenv import load_dotenv
from dataclasses import dataclass
# --- LÍNEA AÑADIDA ---
from typing import Dict, Type, Any

# --- Carga de entorno ---
load_dotenv()

# --- Credenciales y Configuración General ---
SAP_USERNAME = os.getenv("SAP_USER")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")
SAP_BASE_URL = os.getenv("SAP_URL", "https://s4pf.refrival.com/sap/bc/gui/sap/its/webgui?sap-language=ES")
DEFAULT_TIMEOUT = 30000

# --- Configuración del Logger ---
class LogConfig:
    LOGGER_NAME = "sap_automation"
    LOG_LEVEL = "INFO"
    LOG_FILE = "automation.log"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

# --- PASO 1: Importa aquí las clases específicas de cada transacción ---
from pages.mb52_page import MB52Page
from services.mb52_service import MB52Service
from data_models.mb52_models import Mb52FormData
# from pages.iq09_page import IQ09Page # (Ejemplo para el futuro)


# --- PASO 2: Define las clases de configuración para cada transacción ---
class Mb52Config:
    TRANSACTION_CODE = "MB52"
    DEFAULT_CENTRO = "E086"
    DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/home/covi/Descargas")
    EXPORT_FILENAME = "STOCK.xlsx"
    LOCATOR_FILE = "locators/mb52.toml"

# class Iq09Config: # (Ejemplo para el futuro)
#     ...


# --- PASO 3: Define la "Receta" genérica ---
@dataclass
class TransactionRecipe:
    """Contiene todos los 'ingredientes' para construir un servicio de transacción."""
    config_class: Type
    page_class: Type
    service_class: Type
    data_model_class: Type


# --- PASO 4: Registra cada transacción con su receta ---
TRANSACTION_REGISTRY: Dict[str, TransactionRecipe] = {
    "mb52": TransactionRecipe(
        config_class=Mb52Config,
        page_class=MB52Page,
        service_class=MB52Service,
        data_model_class=Mb52FormData,
    ),
    # "iq09": TransactionRecipe(...), # <- Añadir una nueva transacción sería así de fácil
}