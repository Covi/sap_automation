# core/builders/generic_transaction_builder.py

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
    def __init__(self, transaction_name: str):
        if transaction_name not in TRANSACTION_REGISTRY:
            raise ValueError(f"Transacción '{transaction_name}' no reconocida.")
        
        self.recipe = TRANSACTION_REGISTRY[transaction_name]
        self.provider_factory = LocatorProviderFactory()
        
        log.info(f"Builder inicializado para la transacción: {self.recipe.config_class.TRANSACTION_CODE}")

    def build_service(self, page: Page) -> Any:
        """
        Construye y devuelve el servicio para la transacción.
        """
        easy_access_provider = self.provider_factory.create("easy_access.toml")
        
        trx_locator_filename = self.recipe.config_class.LOCATOR_FILE
        trx_provider = self.provider_factory.create(trx_locator_filename)

        easy_access_page = SAPEasyAccessPage(page, locator_provider=easy_access_provider)
        trx_page = self.recipe.page_class(page, locator_provider=trx_provider)

        transaction_service = TransactionService(easy_access_page)
        trx_service = self.recipe.service_class(transaction_service, trx_page)
        
        return trx_service

    def run_service(self, service: Any, params: Dict[str, Any]) -> None:
        """
        Prepara los datos y ejecuta el servicio.
        Pide los defaults al config a través de un método explícito (contrato).
        """
        config = self.recipe.config_class()
        data_model = self.recipe.data_model_class

        try:
            # 1. El builder pide los defaults al objeto config. No sabe cuáles son.
            default_data = config.get_default_data()
            
            # 2. Se fusionan, dando prioridad a los parámetros de la CLI sobre los defaults.
            final_data = default_data | params
            
            datos = data_model(**final_data)

        except ValidationError as e:
            log.error(f"Error de validación en los parámetros: {e}", exc_info=True)
            raise ValueError("Parámetros de entrada inválidos.") from e

        downloads_dir = Path(config.DOWNLOAD_DIR)
        downloads_dir.mkdir(parents=True, exist_ok=True)
        filename = params.get("output") or config.EXPORT_FILENAME
        path_fichero = downloads_dir / filename
        
        log.info(f"Iniciando {config.TRANSACTION_CODE} con los datos: {datos.model_dump(exclude_none=True)}")
        
        service.run(form_data=datos, path=path_fichero, filename=filename)
        
        log.info(f"Proceso de {config.TRANSACTION_CODE} completado.")