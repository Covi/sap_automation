import logging
from typing import Dict, Any
from pathlib import Path
from pydantic import ValidationError
from playwright.sync_api import Page

from core.builders.builder_protocol import BuilderProtocol
from core.providers.locator_provider_factory import LocatorProviderFactory
from pages.sap_easy_access_page import SAPEasyAccessPage
from services.transaction_service import TransactionService
from core.registry import TRANSACTION_REGISTRY

log = logging.getLogger(__name__)

class GenericTransactionBuilder(BuilderProtocol):
    """
    Builder genérico capaz de construir y ejecutar cualquier servicio de transacción
    registrado en el TRANSACTION_REGISTRY.
    """
    def __init__(self, transaction_name: str):
        """
        Inicializa el builder para una transacción específica.

        :param transaction_name: El nombre de la transacción a construir (ej: 'zsin_ordenes').
        """
        if transaction_name not in TRANSACTION_REGISTRY:
            raise ValueError(f"Transacción '{transaction_name}' no reconocida o no registrada.")
        
        self.recipe = TRANSACTION_REGISTRY[transaction_name]
        self.provider_factory = LocatorProviderFactory()
        
        log.info(f"Builder inicializado para la transacción: {self.recipe.config_class.TRANSACTION_CODE}")

    def build_service(self, page: Page) -> Any:
        """
        Construye el servicio para la transacción a partir de su receta.
        Inyecta las dependencias necesarias como páginas y servicios auxiliares.
        """
        easy_access_provider = self.provider_factory.create("easy_access.toml")
        
        trx_locator_filename = self.recipe.config_class.LOCATOR_FILE
        trx_provider = self.provider_factory.create(trx_locator_filename)

        easy_access_page = SAPEasyAccessPage(page, locator_provider=easy_access_provider)
        trx_page = self.recipe.page_class(page, locator_provider=trx_provider)

        transaction_service = TransactionService(easy_access_page)
        trx_service = self.recipe.service_class(
            transaction_service,
            trx_page,
            **(self.recipe.extra_dependencies or {})
        )

        return trx_service

    def run_service(self, service: Any, params: Dict[str, Any]) -> None:
        """
        Ejecuta el servicio con los parámetros proporcionados por la CLI.
        Construye los schemas de criterios y opciones a partir de la receta.
        """
        config = self.recipe.config_class
        criteria_schema = self.recipe.criteria_schema
        options_schema = self.recipe.options_schema  # Puede ser None

        try:
            # Construye el schema de criterios, aplicando valores por defecto del config
            default_data = {"centro": getattr(config, 'DEFAULT_CENTRO', None)}
            final_criteria_data = {k: v for k, v in default_data.items() if v is not None} | params
            criteria = criteria_schema(**final_criteria_data)

        except ValidationError as e:
            log.error(f"Error de validación en los parámetros de criterios: {e}")
            raise ValueError("Parámetros de entrada para criterios inválidos.") from e

        log.info(f"Iniciando {config.TRANSACTION_CODE} con los criterios: {criteria.model_dump(exclude_none=True)}")

        # --- LÓGICA CONDICIONAL ---
        # Decide cómo llamar al servicio basándose en si la receta define un schema de opciones.
        if options_schema:
            # CASO NUEVO (ej: zsin_ordenes): El servicio espera 'criteria' y 'options'.
            try:
                # Prepara los datos para el schema de opciones, obteniendo valores del config y de la CLI.
                options_data = params.copy()
                options_data['output_path'] = Path(config.DOWNLOAD_DIR)
                options_data['output_filename'] = params.get("output") or config.EXPORT_FILENAME
                options = options_schema(**options_data)
                
            except ValidationError as e:
                log.error(f"Error de validación en los parámetros de opciones: {e}")
                raise ValueError("Parámetros de entrada para opciones inválidos.") from e
            
            service.run(criteria=criteria, options=options)
        
        else:
            # CASO ANTIGUO (ej: mb52): El servicio espera 'form_data', 'path' y 'filename'.
            downloads_dir = Path(config.DOWNLOAD_DIR)
            downloads_dir.mkdir(parents=True, exist_ok=True)
            filename = params.get("output") or config.EXPORT_FILENAME
            path_fichero = downloads_dir / filename
            
            service.run(form_data=criteria, path=path_fichero, filename=filename)
        
        log.info(f"Proceso de {config.TRANSACTION_CODE} completado.")