# config/settings.py

from pathlib import Path
from typing import Dict, Optional
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
    # NUEVO: Flag para habilitar la vía rápida por URL
    use_fast_url: bool = True

class Mb52Config(BaseTransactionConfig):
    """Configuración específica para MB52."""
    # Aquí podrías añadir campos únicos para MB52 en el futuro
    pass

class Iq09Config(BaseTransactionConfig):
    """Configuración específica para IQ09."""
    pass

class ZsinOrdenesConfig(BaseTransactionConfig):
    """Configuración específica para ZSIN_ORDENES."""
    use_fast_url: bool = True
    execute_immediately: bool = True # El flag para el asterisco
    # TODO Se podría incluir lo del toolbar_ok_code de DYNP_OKCODE por defecto true    
    # MAPEO FIEL A TU HOJA DE CÁLCULO
    # TODO En el futuro esto podría venir de un archivo externo (JSON, YAML, DB, etc.) 
    # descargado de la hoja de cálculo Google o usando el API de Google Sheets.
    url_field_mapping: Dict[str, str] = {
        "orden_sup": "SO_NUMOR-LOW",
        "sociedad": "SO_EST-LOW",
        "status": "SO_STAT-LOW",
        "puesto": "SO_PUEST-LOW",
        "orden": "SO_AUFNR-LOW",
        "status_equipo": "SO_USER-LOW",
        "estado_objeto": "SO_ORD-LOW",
        "clase": "SO_TIPO-LOW",
        "texto_std": "SO_KTSC-LOW",
        "actividad": "SO_ACTV-LOW",
        "tipo_actividad": "SO_AFAC-LOW",
        "prioridad": "SO_CRIT-LOW",
        "fuera_horario": "SO_FUER-LOW",
        "equipo": "SO_EQUI-LOW",
        "ubicacion": "SO_UBIC-LOW",
        "zona": "SO_ZONA-LOW",
        "cp": "SO_CODPS-LOW",
        "cliente": "SO_CLIEN-LOW",
        "orden_ax": "SO_ORDMN-LOW",
        "fecha": "SO_FECH-LOW",
        "fecha_creacion": "SO_CREA-LOW",
        "fecha_cierre": "SO_FCIER-LOW",
        "fecha_fin_ext": "SO_FEXT-LOW",
        "fecha_inicio_sol": "SO_INCD-LOW",
        "fecha_fin_des": "SO_FIND-LOW",
        "fecha_prim": "SO_PRIM-LOW",
        "fecha_ult": "SO_ULT-LOW",
        "fecha_bb": "SO_BB-LOW",
        "layout": "P_VARI"
    }
    # Resto igual que la padre
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