# core/registry.py

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

# Importamos el Singleton 'settings' y la CLASE BASE para tipado
from config import settings
from config.settings import BaseTransactionConfig

from pages.mb52_page import MB52Page
from schemas.mb52 import Mb52FormData
from services.mb52_service import MB52Service

from pages.iq09_page import Iq09Page
from schemas.iq09 import Iq09FormData
from services.iq09_service import Iq09Service

from pages.zsin_ordenes_page import ZsinOrdenesPage
from schemas.zsin_ordenes import ZsinOrdenesCriteria, ZsinOrdenesExecutionOptions
from services.zsin_ordenes import ZsinOrdenesService

from utils.file_handler import FileHandler
from utils.print_service import PrintService

@dataclass
class TransactionRecipe:
    """
    Define los componentes necesarios para ejecutar una transacción.
    """
    # Aquí pasamos el OBJETO CON DATOS, no la clase.
    # Usamos 'BaseTransactionConfig' como tipo genérico para que acepte Mb52Config, Iq09Config, etc.
    config: BaseTransactionConfig
    
    page_class: Type
    service_class: Type
    criteria_schema: Type
    options_schema: Optional[Type] = None
    extra_dependencies: Optional[Dict[str, Any]] = None

# --- REGISTRO ---
# Aquí conectamos cada clave con su configuración ESPECÍFICA cargada en memoria.
TRANSACTION_REGISTRY: Dict[str, TransactionRecipe] = {
    "mb52": TransactionRecipe(
        config=settings.transactions.mb52,  # Acceso directo tipado (IDE feliz)
        page_class=MB52Page,
        service_class=MB52Service,
        criteria_schema=Mb52FormData,
    ),
    "iq09": TransactionRecipe(
        config=settings.transactions.iq09,
        page_class=Iq09Page,
        service_class=Iq09Service,
        criteria_schema=Iq09FormData,
    ),
   "zsin_ordenes": TransactionRecipe(
       config=settings.transactions.zsin_ordenes,
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