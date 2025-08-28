# Fichero: config.py

import os
from dotenv import load_dotenv

# --- Carga de entorno ---
load_dotenv()

# --- Configuración General ---
SAP_BASE_URL = os.getenv("SAP_URL", "https://s4pf.refrival.com/sap/bc/gui/sap/its/webgui?sap-language=ES")
DEFAULT_TIMEOUT = 30000
# Opciones válidas: "chromium", "firefox", "webkit"
BROWSER = os.getenv("BROWSER", "firefox")

# --- Configuración del Logger ---
class LogConfig:
    LOGGER_NAME = "sap_automation"
    LOG_LEVEL = "INFO"
    LOG_FILE = "automation.log"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

# --- Clases de Configuración por Transacción ---
class Mb52Config:
    ### CAMBIO: Las credenciales ahora son parte de la configuración de la transacción ###
    SAP_USERNAME = os.getenv("SAP_USER")
    SAP_PASSWORD = os.getenv("SAP_PASSWORD")
    
    TRANSACTION_CODE = "MB52"
    DEFAULT_CENTRO = "E086"
    DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/home/covi/Descargas")
    EXPORT_FILENAME = "STOCK.xlsx"
    LOCATOR_FILE = "locators/mb52.toml"

class Iq09Config:
    ### CAMBIO: Cada transacción gestiona sus propias credenciales ###
    SAP_USERNAME = os.getenv("SAP_USER")
    SAP_PASSWORD = os.getenv("SAP_PASSWORD")

    TRANSACTION_CODE = "IQ09"
    DEFAULT_CENTRO = "E086"
    DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/home/covi/Descargas")
    EXPORT_FILENAME = "STOCK_SERIADO.xlsx"
    LOCATOR_FILE = "locators/iq09.toml"