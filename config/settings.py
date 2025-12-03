# config/settings.py

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, SecretStr

# --- 1. CONFIGURACIÓN GENERAL ---
class LoggingSettings(BaseModel):
    logger_name: str
    log_level: str
    log_file: str
    log_format: str

class GeneralSettings(BaseModel):
    base_url: str
    default_timeout: int
    default_browser: str
    default_centro: str
    date_format: str
    download_dir: Optional[Path] = None

# --- 2. JERARQUÍA DE TRANSACCIONES (SOLID: Liskov + Open/Closed) ---

class BaseTransactionConfig(BaseModel):
    """
    Clase Padre. Define lo que TODAS las transacciones tienen en común.
    No se instancia directamente (abstracta conceptualmente).
    """
    transaction_code: str
    export_filename: str
    locator_file: str
    download_dir: Optional[Path] = None

class Mb52Config(BaseTransactionConfig):
    """Configuración específica para MB52."""
    # Aquí podrías añadir campos únicos para MB52 en el futuro
    pass

class Iq09Config(BaseTransactionConfig):
    """Configuración específica para IQ09."""
    pass

class ZsinOrdenesConfig(BaseTransactionConfig):
    """Configuración específica para ZSIN_ORDENES."""
    # Ejemplo: Si esta transacción necesitara un campo extra, lo pondrías aquí
    # layout_variant: str 
    pass

# --- 3. MODELO CONTENEDOR DE TRANSACCIONES ---
class TransactionsCollection(BaseModel):
    """
    Aquí definimos explícitamente qué transacciones soporta el sistema.
    Esto es mejor que un dict genérico porque permite autocompletado y validación estricta.
    """
    mb52: Mb52Config
    iq09: Iq09Config
    zsin_ordenes: ZsinOrdenesConfig

# --- 4. CONFIGURACIÓN GLOBAL ---
class GlobalConfig(BaseModel):
    general: GeneralSettings
    logging: LoggingSettings
    transactions: TransactionsCollection
    
    # Secretos
    sap_username: str
    sap_password: SecretStr