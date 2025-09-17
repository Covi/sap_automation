# Fichero: core/builders/generic_transaction_builder.py

import logging
from typing import Dict, Any
from pathlib import Path
from pydantic import ValidationError
from playwright.sync_api import Page

# ## XXX CAMBIO 1: Se eliminan las importaciones directas de 'registry' y 'settings'.
# Este módulo ya no conoce la ubicación de esos ficheros.

from core.builders.builder_protocol import BuilderProtocol
from core.providers.locator_provider_factory import LocatorProviderFactory
from pages.sap_easy_access_page import SAPEasyAccessPage
from services.transaction_service import TransactionService

log = logging.getLogger(__name__)

class GenericTransactionBuilder(BuilderProtocol):
    """
    Builder genérico y 'puro' que construye servicios de transacción.
    Recibe todas sus dependencias en el constructor (Inyección de Dependencias).
    """
    # ## XXX CAMBIO 2: El constructor ahora recibe las dependencias que necesita.
    def __init__(self, registry: Dict, configs: Dict, provider_factory: LocatorProviderFactory):
        """
        Inicializa el builder inyectando todas sus dependencias.

        :param registry: El diccionario TRANSACTION_REGISTRY.
        :param configs: El diccionario TRANSACTION_CONFIGS.
        :param provider_factory: Una instancia de LocatorProviderFactory.
        """
        self.registry = registry
        self.configs = configs
        self.provider_factory = provider_factory
        log.info("Builder 'puro' (SOLID) inicializado con sus dependencias.")

    # ## XXX CAMBIO 3: El método ahora recibe el 'transaction_code' como parámetro.
    # El builder ya no tiene estado interno; es una fábrica.
    def build_service(self, transaction_code: str, page: Page) -> Any:
        """
        Construye el servicio para una transacción específica.
        """
        if transaction_code not in self.registry:
            raise ValueError(f"Transacción '{transaction_code}' no reconocida o no registrada.")

        # Obtiene la receta y la configuración usando el código de transacción.
        recipe = self.registry[transaction_code]
        config = self.configs[transaction_code]

        log.info(f"Construyendo servicio para la transacción: {config.transaction_code}")

        easy_access_provider = self.provider_factory.create("easy_access.toml")
        trx_locator_filename = config.locator_file.name
        trx_provider = self.provider_factory.create(trx_locator_filename)

        easy_access_page = SAPEasyAccessPage(page, locator_provider=easy_access_provider)
        
        # Inyectamos el provider y la configuración en la página.
        trx_page = recipe.page_class(page, locator_provider=trx_provider, config=config)

        transaction_service = TransactionService(easy_access_page)

        # Inyectamos la configuración en el servicio final.
        trx_service = recipe.service_class(
            transaction_service=transaction_service,
            page=trx_page,
            config=config,
            **(recipe.extra_dependencies or {})
        )

        return trx_service

    # ## XXX CAMBIO 4: El método también recibe el 'transaction_code'.
    def run_service(self, service: Any, transaction_code: str, params: Dict[str, Any]) -> None:
        """
        Ejecuta el servicio con los parámetros proporcionados.
        """
        config = self.configs[transaction_code]
        recipe = self.registry[transaction_code]

        criteria_schema = recipe.criteria_schema
        options_schema = recipe.options_schema

        try:
            default_data = {"centro": config.default_centro}
            final_criteria_data = default_data | params
            criteria = criteria_schema(**final_criteria_data)
        except ValidationError as e:
            log.error(f"Error de validación en los parámetros de criterios: {e}")
            raise ValueError("Parámetros de entrada para criterios inválidos.") from e

        log.info(f"Iniciando {config.transaction_code} con los criterios: {criteria.model_dump(exclude_none=True)}")

        if options_schema:
            try:
                options_data = params.copy()
                options_data['output_path'] = Path(config.download_dir)
                options_data['output_filename'] = params.get("output") or config.export_filename
                options = options_schema(**options_data)
            except ValidationError as e:
                log.error(f"Error de validación en los parámetros de opciones: {e}")
                raise ValueError("Parámetros de entrada para opciones inválidos.") from e
            
            service.run(criteria=criteria, options=options)
        else:
            downloads_dir = Path(config.download_dir)
            downloads_dir.mkdir(parents=True, exist_ok=True)
            filename = params.get("output") or config.export_filename
            path_fichero = downloads_dir / filename
            
            service.run(form_data=criteria, path=path_fichero, filename=filename)
        
        log.info(f"Proceso de {config.transaction_code} completado.")