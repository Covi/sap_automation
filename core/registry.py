# Fichero: registry.py
# Descripción: Registro central de transacciones para evitar importaciones circulares y facilitar la construcción de servicios.

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

# ===================================================================
# 1. IMPORTACIÓN DE CONFIGURACIÓN
# ===================================================================
# CAMBIO 1: Se importa el diccionario de configuraciones y el tipo base.
# Ya no se importan clases específicas como Mb52Config, pues no existen.
from config.settings import TRANSACTION_CONFIGS, TransactionConfig

# ===================================================================
# 2. IMPORTACIÓN DE COMPONENTES DE TRANSACCIÓN
# ===================================================================
# --- Componentes para MB52 ---
from pages.mb52_page import MB52Page
from schemas.mb52 import Mb52FormData
from services.mb52_service import MB52Service

# --- Componentes para IQ09 ---
from pages.iq09_page import Iq09Page
from schemas.iq09 import Iq09FormData
from services.iq09_service import Iq09Service

# --- Componentes para ZSIN_ORDENES ---
from pages.zsin_ordenes_page import ZsinOrdenesPage
from schemas.zsin_ordenes import ZsinOrdenesCriteria, ZsinOrdenesExecutionOptions
from services.zsin_ordenes_service import ZsinOrdenesService

# --- Dependencias extra ---
from utils.file_handler import FileHandler
from utils.print_service import PrintService

# ===================================================================
# 3. DEFINICIÓN DE LA "RECETA" DE TRANSACCIÓN
# ===================================================================

@dataclass(frozen=True)
class TransactionRecipe:
    """
    Contiene todos los 'ingredientes' necesarios para construir
    un servicio de transacción.
    
    A diferencia de la versión anterior, ahora recibe la configuración
    ya instanciada, cumpliendo con el principio de Inversión de Dependencias.
    """
    # CAMBIO 2: Reemplazamos 'config_class' por la instancia de configuración.
    # El registro ya no es responsable de saber cómo crear la config.
    config: TransactionConfig
    
    page_class: Type
    service_class: Type
    criteria_schema: Type
    options_schema: Optional[Type] = None
    extra_dependencies: Optional[Dict[str, Any]] = None

# ===================================================================
# 4. REGISTRO CENTRALIZADO DE TRANSACCIONES
# ===================================================================

TRANSACTION_REGISTRY: Dict[str, TransactionRecipe] = {
    # CAMBIO 3: La clave del registro ahora coincide con el nombre de la 
    # sección en el fichero 'config.toml' para mayor consistencia.
    "mb52": TransactionRecipe(
        # CAMBIO 4: Se obtiene la configuración directamente del diccionario importado.
        # La clave ("MB52") es el 'transaction_code' definido en el TOML.
        config=TRANSACTION_CONFIGS["MB52"],
        page_class=MB52Page,
        service_class=MB52Service,
        criteria_schema=Mb52FormData,
    ),
    "iq09": TransactionRecipe(
        config=TRANSACTION_CONFIGS["IQ09"],
        page_class=Iq09Page,
        service_class=Iq09Service,
        criteria_schema=Iq09FormData,
    ),
    "zsin_ordenes": TransactionRecipe(
        config=TRANSACTION_CONFIGS["ZSIN_ORDENES"],
        page_class=ZsinOrdenesPage,
        service_class=ZsinOrdenesService,
        criteria_schema=ZsinOrdenesCriteria,
        options_schema=ZsinOrdenesExecutionOptions,
        extra_dependencies={
            "file_handler": FileHandler(),
            "print_service": PrintService()
        },
    ),
}