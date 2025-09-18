# Fichero: config/settings.py

import toml
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# ===================================================================
# 1. MODELO PARA SECRETOS Y VARIABLES DE ENTORNO
# ===================================================================

class EnvironmentSettings(BaseSettings):
    """
    Este modelo lee automáticamente las variables del fichero .env.
    Pydantic se encarga de validar que existan. ¡Esto reemplaza a get_required_env!
    """
    sap_username: str = Field(alias="SAP_USER")
    sap_password: str = Field(alias="SAP_PASSWORD", repr=False)

    class Config:
        # Fichero del que se leerán las variables de entorno
        env_file = ".env"
        env_file_encoding = "utf-8"

# ===================================================================
# 2. MODELOS PARA LA CONFIGURACIÓN DEL FICHERO .TOML
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
    download_dir: Path | None = None

class AllTransactions(BaseModel):
    mb52: TransactionSettings
    iq09: TransactionSettings
    zsin_ordenes: TransactionSettings

# XXX Config final
class AppSettings(BaseModel):
    """El modelo raíz que mapea la estructura de configuración de la aplicación."""
    general: GeneralSettings
    logging: LoggingSettings
    transactions: AllTransactions

# ===================================================================
# 3. CARGA Y COMBINACIÓN DE TODA LA CONFIGURACIÓN
# ===================================================================

# --- Rutas del Proyecto ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCATORS_DIR = PROJECT_ROOT / "locators"

# --- Carga de las diferentes fuentes ---
_config_path = Path(__file__).parent / "config.toml"
_raw_toml_data = toml.load(_config_path)

# --- Instanciación y Validación ---
env_settings = EnvironmentSettings()   # Pydantic lee y valida .env aquí # type: ignore
app_settings = AppSettings(**_raw_toml_data)  # Pydantic valida el diccionario del toml

# ===================================================================
# 4. EXPORTACIÓN DE LAS CONFIGURACIONES FINALES
# ===================================================================
from dataclasses import dataclass

@dataclass(frozen=True)
class TransactionConfig:
    download_dir: Path
    default_centro: str
    date_format: str
    transaction_code: str
    export_filename: str
    locator_file: Path
    sap_username: str = Field(repr=False)
    sap_password: str = Field(repr=False)


TRANSACTION_CONFIGS = {}
for tx_name, tx_data in app_settings.transactions:
    final_download_dir = tx_data.download_dir or app_settings.general.download_dir
    
    tx_config = TransactionConfig(
        download_dir=final_download_dir,
        default_centro=app_settings.general.default_centro,
        date_format=app_settings.general.date_format,
        transaction_code=tx_data.transaction_code,
        export_filename=tx_data.export_filename,
        locator_file=LOCATORS_DIR / tx_data.locator_file,
        sap_username=env_settings.sap_username,
        sap_password=env_settings.sap_password
    )
    TRANSACTION_CONFIGS[tx_data.transaction_code] = tx_config

# Exportamos el resto de configs
general_config = app_settings.general
log_config = app_settings.logging