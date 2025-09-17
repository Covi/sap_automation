# Fichero: config/settings.py

import toml
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dataclasses import dataclass

# ===================================================================
# DEFINICIONES ESTRUCTURALES Y DE CONSTANTES
# ===================================================================

class EnvConfig:
    """Contiene los nombres de las variables de entorno requeridas."""
    USER_VAR = "SAP_USER"
    PASSWORD_VAR = "SAP_PASSWORD"

class PathConfig:
    """Contiene las rutas y nombres de ficheros fijos del proyecto."""
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    LOCATORS_DIR = PROJECT_ROOT / "locators"
    CONFIG_FILENAME = "config.toml"

# Exponemos la variable a nivel de módulo para que otros ficheros
# puedan hacer "from config.settings import LOCATORS_DIR" sin necesidad
# de conocer la estructura interna de la clase PathConfig.
LOCATORS_DIR = PathConfig.LOCATORS_DIR


# --- Carga de las diferentes fuentes ---
_config_path = Path(__file__).parent / PathConfig.CONFIG_FILENAME
_raw_toml_data = toml.load(_config_path)


# ===================================================================
# MODELO PARA SECRETOS Y VARIABLES DE ENTORNO
# ===================================================================

class EnvironmentSettings(BaseSettings):
    """
    Este modelo lee automáticamente las variables del fichero .env.
    """
    sap_username: str = Field(alias=EnvConfig.USER_VAR)
    sap_password: str = Field(alias=EnvConfig.PASSWORD_VAR, repr=False)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# ===================================================================
# MODELOS PARA LA CONFIGURACIÓN DEL FICHERO .TOML
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
# CARGA Y COMBINACIÓN DE TODA LA CONFIGURACIÓN
# ===================================================================

# --- Instanciación y Validación ---
env_settings = EnvironmentSettings()  # type: ignore
toml_settings = TomlSettings(**_raw_toml_data)

# ===================================================================
# EXPORTACIÓN DE LAS CONFIGURACIONES FINALES
# (Usando dataclasses para desacoplar del resto de la app)
# ===================================================================

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
for tx_name, tx_data in toml_settings.transactions:
    final_download_dir = tx_data.download_dir or toml_settings.general.download_dir
    
    tx_config = TransactionConfig(
        download_dir=final_download_dir,
        default_centro=toml_settings.general.default_centro,
        date_format=toml_settings.general.date_format,
        transaction_code=tx_data.transaction_code,
        export_filename=tx_data.export_filename,
        locator_file=LOCATORS_DIR / tx_data.locator_file, # Usamos la variable exportada
        sap_username=env_settings.sap_username,
        sap_password=env_settings.sap_password
    )
    TRANSACTION_CONFIGS[tx_data.transaction_code] = tx_config

# Exportamos el resto de configs para uso global
log_config = toml_settings.logging
general_config = toml_settings.general