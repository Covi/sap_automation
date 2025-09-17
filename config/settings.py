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


class TomlSettings(BaseModel):
    """El modelo raíz que mapea la estructura del fichero config.toml."""
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
toml_settings = TomlSettings(**_raw_toml_data) # Pydantic lee y valida el diccionario de toml aquí

# ===================================================================
# 4. EXPORTACIÓN DE LAS CONFIGURACIONES FINALES
#    (Usando dataclasses para desacoplar del resto de la app, como antes)
# ===================================================================
from dataclasses import dataclass

@dataclass(frozen=True)
class TransactionConfig:
    # ... (La definición de la dataclass es la misma que la versión corregida)
    download_dir: Path
    default_centro: str
    date_format: str
    transaction_code: str
    export_filename: str
    locator_file: Path
    sap_username: str = Field(repr=False)
    sap_password: str = Field(repr=False)


TRANSACTION_CONFIGS = {}
for tx_name, tx_data in toml_settings.transactions:
    final_download_dir = tx_data.download_dir or toml_settings.general.download_dir
    
    tx_config = TransactionConfig(
        # Los datos vienen de los modelos de pydantic ya validados
        download_dir=final_download_dir,
        default_centro=toml_settings.general.default_centro,
        date_format=toml_settings.general.date_format,
        transaction_code=tx_data.transaction_code,
        export_filename=tx_data.export_filename,
        locator_file=LOCATORS_DIR / tx_data.locator_file,
        sap_username=env_settings.sap_username,
        sap_password=env_settings.sap_password
    )
    TRANSACTION_CONFIGS[tx_data.transaction_code] = tx_config

# Exportamos el resto de configs
log_config = toml_settings.logging
general_config = toml_settings.general