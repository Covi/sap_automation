# config.py
# Configuración general y de transacciones para la automatización de SAP

import os
from dotenv import load_dotenv

# Carga las variables del fichero .env en el entorno
load_dotenv()

# --- Credenciales ---
SAP_USERNAME = os.getenv("SAP_USER")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")
# Si quisieras acceder a los otros usuarios, podrías hacerlo igual:
# SAP_USERNAME_1 = os.getenv("SAP_USER1")
# SAP_PASSWORD_1 = os.getenv("SAP_PASSWORD1")

# --- Configuración General de SAP ---
SAP_BASE_URL = os.getenv("SAP_URL", "https://s4pf.refrival.com/sap/bc/gui/sap/its/webgui?sap-language=ES")
DEFAULT_TIMEOUT = 30000

# --- Configuración del Logger ---
class LogConfig:
    """Configuraciones para el logger de la aplicación."""
    LOGGER_NAME = "sap_automation"
    LOG_LEVEL = "INFO"  # Cambiar a "DEBUG" para ver más detalles
    LOG_FILE = "automation.log"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

# --- Configuración por Transacción ---
class Mb52Config:
    TRANSACTION_CODE = "MB52"
    DEFAULT_CENTRO = "E086"
    DOWNLOAD_DIR = "/home/covi/Descargas"
    EXPORT_FILENAME = "STOCK.xlsx"

# Aquí añadiríamos clases de config para otras transacciones como Iq09Config, etc.