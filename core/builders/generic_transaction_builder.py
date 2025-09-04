# core/builders/generic_builder.py

from pathlib import Path
from typing import Dict, Any
from pydantic import ValidationError
from playwright.sync_api import Page

from core.builders.builder_protocol import BuilderProtocol
# CAMBIO: Ya NO se importa TomlLocatorProvider ni CompositeLocatorProvider
from core.providers.locator_provider_factory import LocatorProviderFactory
from pages.sap_login_page import SAPLoginPage
from pages.sap_easy_access_page import SAPEasyAccessPage
from services.login_service import LoginService
from services.transaction_service import TransactionService
from utils.logger import log
from core.registry import TRANSACTION_REGISTRY

class GenericTransactionBuilder(BuilderProtocol):
    def __init__(self, transaction_name: str):
        if transaction_name not in TRANSACTION_REGISTRY:
            raise ValueError(f"Transacción '{transaction_name}' no reconocida o no registrada.")

        self.recipe = TRANSACTION_REGISTRY[transaction_name]
        # CAMBIO: El builder ahora crea y posee la factory.
        # La factory es la única que sabe cómo construir los providers.
        self.provider_factory = LocatorProviderFactory(self.recipe)
        
        log.info(f"Builder inicializado para la transacción: {self.recipe.config_class.TRANSACTION_CODE}")

    def build_service(self, page: Page) -> Any:
        """Construye y devuelve el servicio adecuado para la transacción."""
        
        # CAMBIO: El builder ya no construye providers, se los pide a su factory.
        login_provider, easy_access_provider, tx_provider = self.provider_factory.create_providers()

        # El resto del código permanece igual, pero ahora opera sobre abstracciones
        # que le han sido proporcionadas, sin saber cómo se crearon.
        login_page = SAPLoginPage(page, locator_provider=login_provider)
        easy_access_page = SAPEasyAccessPage(page, locator_provider=easy_access_provider)
        tx_page = self.recipe.page_class(page, locator_provider=tx_provider)

        login_service = LoginService(login_page, easy_access_page)
        transaction_service = TransactionService(easy_access_page)
        tx_service = self.recipe.service_class(transaction_service, tx_page)

        config = self.recipe.config_class
        login_service.login(config.SAP_USERNAME, config.SAP_PASSWORD)
        
        return tx_service

    def run_service(self, service: Any, params: Dict[str, Any]) -> None:
        """
        Ejecuta el servicio con los datos y configuración proporcionados.
        Este método no sufre cambios.
        """
        config = self.recipe.config_class
        data_model = self.recipe.data_model_class

        try:
            default_data = {"centro": getattr(config, 'DEFAULT_CENTRO', None)}
            final_data = {k: v for k, v in default_data.items() if v is not None} | params
            datos = data_model(**final_data)
        except ValidationError as e:
            log.error(f"Error de validación en los parámetros: {e}")
            raise ValueError("Parámetros de entrada inválidos.") from e

        downloads_dir = Path(config.DOWNLOAD_DIR)
        downloads_dir.mkdir(parents=True, exist_ok=True)
        filename = params.get("output") or config.EXPORT_FILENAME
        path_fichero = downloads_dir / filename
        
        log.info(f"Iniciando {config.TRANSACTION_CODE} con los datos: {datos.model_dump(exclude_none=True)}")
        
        service.run(form_data=datos, path=path_fichero, filename=filename)
        
        log.info(f"Proceso de {config.TRANSACTION_CODE} completado.")