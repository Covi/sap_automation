# Descripción: Registro central de transacciones para evitar importaciones circulares.

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

# --- Importa las clases de configuración desde config.py ---
from config import Mb52Config, Iq09Config, ZsinOrdenesConfig

# --- Importa todos los componentes específicos de las transacciones ---
from pages.mb52_page import MB52Page
from schemas.mb52 import Mb52FormData
from services.mb52_service import MB52Service

from pages.iq09_page import Iq09Page
from schemas.iq09 import Iq09FormData
from services.iq09_service import Iq09Service

from pages.zsin_ordenes_page import ZsinOrdenesPage
# CAMBIO 1: Importamos también el schema de opciones
from schemas.zsin_ordenes import ZsinOrdenesCriteria, ZsinOrdenesExecutionOptions
from services.zsin_ordenes_service import ZsinOrdenesService

# --- Dependencias extra ---
from utils.file_handler import FileHandler
from utils.print_service import PrintService


# CAMBIO 2: La "Receta" ahora es semánticamente más explícita
@dataclass
class TransactionRecipe:
    """Contiene todos los 'ingredientes' para construir un servicio de transacción."""
    config_class: Type
    page_class: Type
    service_class: Type
    # Se reemplaza 'data_model_class' por dos campos específicos
    criteria_schema: Type
    options_schema: Optional[Type] = None  # Opcional para transacciones antiguas
    extra_dependencies: Optional[Dict[str, Any]] = None


# --- Registra cada transacción con su receta ---
TRANSACTION_REGISTRY: Dict[str, TransactionRecipe] = {
    "mb52": TransactionRecipe(
        config_class=Mb52Config,
        page_class=MB52Page,
        service_class=MB52Service,
        # CAMBIO 3: Las transacciones antiguas usan el nuevo campo 'criteria_schema'
        criteria_schema=Mb52FormData,
    ),
    "iq09": TransactionRecipe(
        config_class=Iq09Config,
        page_class=Iq09Page,
        service_class=Iq09Service,
        criteria_schema=Iq09FormData,
    ),
   "zsin_ordenes": TransactionRecipe(
       config_class=ZsinOrdenesConfig,
       page_class=ZsinOrdenesPage,
       service_class=ZsinOrdenesService,
       # CAMBIO 4: La nueva transacción usa ambos campos para schemas
       criteria_schema=ZsinOrdenesCriteria,
       options_schema=ZsinOrdenesExecutionOptions,
       extra_dependencies={
           "file_handler": FileHandler(),
           "print_service": PrintService()
        }
   ),
}