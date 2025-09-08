# core/builders/generic_transaction_builder.py

# Logging
import logging
log = logging.getLogger(__name__)

from typing import Dict, Any
from pathlib import Path
from pydantic import ValidationError
from playwright.sync_api import Page

from core.builders.builder_protocol import BuilderProtocol
from core.providers.locator_provider_factory import LocatorProviderFactory
from pages.sap_login_page import SAPLoginPage
from pages.sap_easy_access_page import SAPEasyAccessPage
from services.login_service import LoginService
from services.transaction_service import TransactionService
from core.registry import TRANSACTION_REGISTRY

class GenericTransactionBuilder(BuilderProtocol):
    """
    Construye el servicio completo para ejecutar una transacción SAP específica.
    Utiliza una factory para crear los proveedores de localizadores necesarios,
    manteniendo el builder desacoplado de la implementación de los providers.
    """
    def __init__(self, transaction_name: str):
        if transaction_name not in TRANSACTION_REGISTRY:
            raise ValueError(f"Transacción '{transaction_name}' no reconocida o no registrada.")
        
        self.recipe = TRANSACTION_REGISTRY[transaction_name]
        self.provider_factory = LocatorProviderFactory()
        
        log.info(f"Builder inicializado para la transacción: {self.recipe.config_class.TRANSACTION_CODE}")

    def build_service(self, page: Page) -> Any:
        """Construye y devuelve el servicio adecuado para la transacción."""
        
        # El builder pide a la factory los providers que necesita, uno por uno.
        # Es explícito sobre sus dependencias sin saber cómo se construyen.
        login_provider = self.provider_factory.create("login.toml")
        easy_access_provider = self.provider_factory.create("easy_access.toml")
        
        trx_locator_filename = self.recipe.config_class.LOCATOR_FILE
        trx_provider = self.provider_factory.create(trx_locator_filename)

        # Construcción de las páginas con sus respectivos providers
        login_page = SAPLoginPage(page, locator_provider=login_provider)
        easy_access_page = SAPEasyAccessPage(page, locator_provider=easy_access_provider)
        trx_page = self.recipe.page_class(page, locator_provider=trx_provider)

        # Composición de los servicios
        login_service = LoginService(login_page, easy_access_page)
        transaction_service = TransactionService(easy_access_page)
        trx_service = self.recipe.service_class(transaction_service, trx_page)

        # El builder también orquesta el flujo inicial (login)
        config = self.recipe.config_class
        login_service.login(config.SAP_USERNAME, config.SAP_PASSWORD)
        
        return trx_service

    def run_service(self, service: Any, params: Dict[str, Any]) -> None:
        """
        Ejecuta el servicio con los datos y configuración proporcionados.
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