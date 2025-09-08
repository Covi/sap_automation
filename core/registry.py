# Fichero: core/registry.py
# Descripción: Registro central de transacciones para evitar importaciones circulares.

from dataclasses import dataclass
from typing import Dict, Type, Any

# --- Importa las clases de configuración desde config.py ---
from config import Mb52Config, Iq09Config

# --- Importa todos los componentes específicos de las transacciones ---
from pages.mb52_page import MB52Page
from services.mb52_service import MB52Service
from data_models.mb52_models import Mb52FormData

from pages.iq09_page import Iq09Page
from services.iq09_service import Iq09Service
from data_models.iq09_models import Iq09FormData


# --- Define la "Receta" genérica ---
@dataclass
class TransactionRecipe:
    """Contiene todos los 'ingredientes' para construir un servicio de transacción."""
    config_class: Type
    page_class: Type
    service_class: Type
    data_model_class: Type


# --- Registra cada transacción con su receta ---
TRANSACTION_REGISTRY: Dict[str, TransactionRecipe] = {
    "mb52": TransactionRecipe(
        config_class=Mb52Config,
        page_class=MB52Page,
        service_class=MB52Service,
        data_model_class=Mb52FormData,
    ),
    "iq09": TransactionRecipe(
        config_class=Iq09Config,
        page_class=Iq09Page,
        service_class=Iq09Service,
        data_model_class=Iq09FormData,
    ),
#    "zsin_ordenes": TransactionRecipe(
#        config_class=ZSIN_OrdenesConfig,
#        page_class=ZSIN_OrdenesPage,
#        service_class=ZSIN_OrdenesService,
#        data_model_class=ZSIN_OrdenesFormData,
#    ),
}