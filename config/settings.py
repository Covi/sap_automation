# Fichero: config/settings.py

import os
import toml
from pathlib import Path
from dotenv import load_dotenv

from pydantic import BaseModel, Field

# --- Carga de entorno para secretos (.env) ---
load_dotenv()

# --- Definición de Rutas del Proyecto ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCATORS_DIR = PROJECT_ROOT / "locators"

# ===================================================================
# 1. DEFINICIÓN DE LOS MODELOS DE CONFIGURACIÓN CON PYDANTIC
#    Estas clases actúan como el "esquema" de tu fichero config.toml
# ===================================================================

class GeneralSettings(BaseModel):
    base_url: str
    default_timeout: int
    default_browser: str
    download_dir: Path
    default_centro: str
    date_format: str

class LoggingSettings(BaseModel):
    logger_name: str
    log_level: str
    log_file: str
    log_format: str

class TransactionSettings(BaseModel):
    transaction_code: str
    export_filename: str
    locator_file: str
    # Este campo es opcional. Si no está en el .toml, será None.
    download_dir: Path | None = None

class AllTransactions(BaseModel):
    """Define explícitamente cada transacción que esperas encontrar."""
    mb52: TransactionSettings
    iq09: TransactionSettings
    zsin_ordenes: TransactionSettings = Field(alias="zsin-ordenes") # Si usas guiones en el toml

class AppSettings(BaseModel):
    """El modelo raíz que contiene toda la configuración."""
    general: GeneralSettings
    logging: LoggingSettings
    transactions: AllTransactions

# ===================================================================
# 2. CARGA Y VALIDACIÓN DE LA CONFIGURACIÓN
# ===================================================================

_config_path = Path(__file__).parent / "config.toml"
_raw_config_data = toml.load(_config_path)

# ¡Magia de Pydantic! Se parsea y valida todo el diccionario con una sola línea.
# Si algo en el .toml no coincide con los modelos, Pydantic lanzará un error.
settings = AppSettings(**_raw_config_data)

# ===================================================================
# 3. (Opcional) AÑADIR CREDENCIALES Y EXPORTAR OBJETOS FINALES
#    Para mantener la configuración de transacciones limpia, podemos
#    crear las instancias finales como lo hacíamos antes.
# ===================================================================

from dataclasses import dataclass

@dataclass(frozen=True)
class TransactionConfig:
    """Dataclass final para usar en la aplicación (igual que la que tenías)."""
    download_dir: Path
    default_centro: str
    date_format: str
    transaction_code: str
    export_filename: str
    locator_file: Path
    sap_username: str = Field(repr=False)
    sap_password: str = Field(repr=False)

# --- Creación de las instancias finales ---

TRANSACTION_CONFIGS = {}
for tx_name, tx_data in settings.transactions:
    # Ahora tx_data es un objeto TransactionSettings con tipos conocidos
    
    # Lógica para determinar el directorio de descarga
    final_download_dir = tx_data.download_dir or settings.general.download_dir
    
    tx_config = TransactionConfig(
        sap_username=os.getenv("SAP_USER", ""), # Añadimos un default para que Pylance no se queje
        sap_password=os.getenv("SAP_PASSWORD", ""),
        download_dir=final_download_dir,
        default_centro=settings.general.default_centro,
        date_format=settings.general.date_format,
        transaction_code=tx_data.transaction_code,
        export_filename=tx_data.export_filename,
        locator_file=LOCATORS_DIR / tx_data.locator_file
    )
    TRANSACTION_CONFIGS[tx_data.transaction_code] = tx_config

# También puedes exportar configuraciones específicas si quieres
log_config = settings.logging
general_config = settings.general