# Fichero: registry.py
# Descripción: Registro central de "recetas" para construir servicios de transacción.

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

# --- 1. YA NO SE IMPORTA NADA DE 'config' ---
# Las clases de configuración ya no son necesarias aquí.

# --- Importa todos los componentes específicos de las transacciones ---
from pages.mb52_page import MB52Page
from schemas.mb52 import Mb52FormData
from services.mb52_service import MB52Service

from pages.iq09_page import Iq09Page
from schemas.iq09 import Iq09FormData
from services.iq09_service import Iq09Service

from pages.zsin_ordenes_page import ZsinOrdenesPage
from schemas.zsin_ordenes import ZsinOrdenesCriteria, ZsinOrdenesExecutionOptions
from services.zsin_ordenes_service import ZsinOrdenesService

# --- Dependencias extra ---
from utils.file_handler import FileHandler
from utils.print_service import PrintService


@dataclass
class TransactionRecipe:
    """
    Contiene todos los 'planos' para construir un servicio de transacción.
    Ya no contiene la configuración.
    """
    # --- 2. EL CAMPO 'config_class' SE ELIMINA ---
    page_class: Type
    service_class: Type
    criteria_schema: Type
    options_schema: Optional[Type] = None
    extra_dependencies: Optional[Dict[str, Any]] = None


# --- Registra cada transacción con su receta simplificada ---
TRANSACTION_REGISTRY: Dict[str, TransactionRecipe] = {
    "MB52": TransactionRecipe(
        # --- 3. SE ELIMINA LA LÍNEA 'config_class' ---
        page_class=MB52Page,
        service_class=MB52Service,
        criteria_schema=Mb52FormData,
    ),
    "IQ09": TransactionRecipe(
        page_class=Iq09Page,
        service_class=Iq09Service,
        criteria_schema=Iq09FormData,
    ),
   "ZSIN_ORDENES": TransactionRecipe(
       page_class=ZsinOrdenesPage,
       service_class=ZsinOrdenesService,
       criteria_schema=ZsinOrdenesCriteria,
       options_schema=ZsinOrdenesExecutionOptions,
       extra_dependencies={
           "file_handler": FileHandler(),
           "print_service": PrintService()
        }
   ),
}