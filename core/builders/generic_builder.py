# Fichero: core/builders/generic_builder.py

from pathlib import Path
from typing import Dict, Any
from pydantic import ValidationError
from playwright.sync_api import Page

# --- Imports genéricos de la aplicación ---
from core.builders.builder_protocol import BuilderProtocol
from core.providers.toml_provider import TomlLocatorProvider
from core.providers.composite_provider import CompositeLocatorProvider
from pages.sap_login_page import SAPLoginPage
from pages.sap_easy_access_page import SAPEasyAccessPage
from services.login_service import LoginService
from services.transaction_service import TransactionService
from utils.logger import log

# --- Imports de configuración ---
from config import TRANSACTION_REGISTRY, SAP_USERNAME, SAP_PASSWORD

class GenericTransactionBuilder(BuilderProtocol):
    """
    Un builder genérico que construye el servicio para cualquier transacción
    registrada en TRANSACTION_REGISTRY.
    """
    def __init__(self, transaction_name: str):
        if transaction_name not in TRANSACTION_REGISTRY:
            raise ValueError(f"Transacción '{transaction_name}' no reconocida o no registrada en config.py.")
        self.recipe = TRANSACTION_REGISTRY[transaction_name]
        log.info(f"Builder inicializado para la transacción: {self.recipe.config_class.TRANSACTION_CODE}")

    def build_service(self, page: Page) -> Any:
        # Lógica de construcción genérica usando la receta
        common_provider = TomlLocatorProvider("locators/common.toml")
        login_provider = TomlLocatorProvider("locators/login.toml")
        easy_access_provider = TomlLocatorProvider("locators/easy_access.toml")
        
        tx_provider = TomlLocatorProvider(self.recipe.config_class.LOCATOR_FILE)
        
        composite_easy_access = CompositeLocatorProvider([easy_access_provider, common_provider])
        composite_tx = CompositeLocatorProvider([tx_provider, common_provider])

        login_page = SAPLoginPage(page, locator_provider=login_provider)
        easy_access_page = SAPEasyAccessPage(page, locator_provider=composite_easy_access)
        
        tx_page = self.recipe.page_class(page, locator_provider=composite_tx)

        login_service = LoginService(login_page, easy_access_page)
        transaction_service = TransactionService(easy_access_page)
        
        tx_service = self.recipe.service_class(transaction_service, tx_page)

        login_service.login(SAP_USERNAME, SAP_PASSWORD)
        return tx_service

    def run_service(self, service: Any, params: Dict[str, Any]) -> None:
        # Lógica de ejecución genérica usando la receta
        config = self.recipe.config_class
        data_model = self.recipe.data_model_class

        try:
            default_data = {"centro": getattr(config, 'DEFAULT_CENTRO', None)}
            # Filtra los defaults que son None y los une con los params del usuario
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
        
        service.generar_informe(datos)
        service.descargar_informe(str(path_fichero), filename)
        
        log.info(f"Informe de {config.TRANSACTION_CODE} descargado en: {path_fichero}")