# Fichero: core/builders/generic_builder.py

from pathlib import Path
from typing import Dict, Any
from pydantic import ValidationError
from playwright.sync_api import Page

from core.builders.builder_protocol import BuilderProtocol
from core.providers.toml_provider import TomlLocatorProvider
from core.providers.composite_provider import CompositeLocatorProvider
from pages.sap_login_page import SAPLoginPage
from pages.sap_easy_access_page import SAPEasyAccessPage
from services.login_service import LoginService
from services.transaction_service import TransactionService
from utils.logger import log

from core.registry import TRANSACTION_REGISTRY

class GenericTransactionBuilder(BuilderProtocol):
    def __init__(self, transaction_name: str):
        if transaction_name not in TRANSACTION_REGISTRY:
            raise ValueError(f"Transacción '{transaction_name}' no reconocida o no registrada en core/registry.py.")
        self.recipe = TRANSACTION_REGISTRY[transaction_name]
        log.info(f"Builder inicializado para la transacción: {self.recipe.config_class.TRANSACTION_CODE}")

    def build_service(self, page: Page) -> Any:
        """
        Construye y devuelve el servicio adecuado para la transacción.
        """
        project_root = Path(__file__).resolve().parent.parent.parent

        # --- CAMBIOS SUGERIDOS ---
        # Usando el operador / de pathlib, que es la forma correcta de unir rutas.

        # 1. Rutas a los ficheros de locators comunes
        common_locators_path = project_root / "locators" / "common.toml"
        login_locators_path = project_root / "locators" / "login.toml"
        easy_access_locators_path = project_root / "locators" / "easy_access.toml" # Errata corregida

        # 2. Ruta al fichero específico de la transacción (BUG CORREGIDO)
        tx_locator_filename = self.recipe.config_class.LOCATOR_FILE
        tx_locators_path = project_root / tx_locator_filename

        # 3. Creación de providers con las rutas absolutas y corregidas
        common_provider = TomlLocatorProvider(common_locators_path)
        login_provider = TomlLocatorProvider(login_locators_path)
        easy_access_provider = TomlLocatorProvider(easy_access_locators_path)
        tx_provider = TomlLocatorProvider(tx_locators_path)
        # --- FIN DE CAMBIOS SUGERIDOS ---

        composite_easy_access = CompositeLocatorProvider([easy_access_provider, common_provider])
        composite_tx = CompositeLocatorProvider([tx_provider, common_provider])

        login_page = SAPLoginPage(page, locator_provider=login_provider)
        easy_access_page = SAPEasyAccessPage(page, locator_provider=composite_easy_access)
        tx_page = self.recipe.page_class(page, locator_provider=composite_tx)
        tx_page = self.recipe.page_class(page, locator_provider=composite_tx)

        login_service = LoginService(login_page, easy_access_page)
        transaction_service = TransactionService(easy_access_page)
        tx_service = self.recipe.service_class(transaction_service, tx_page)

        ### CAMBIO: Lee las credenciales de la receta específica de la transacción ###
        config = self.recipe.config_class
        login_service.login(config.SAP_USERNAME, config.SAP_PASSWORD)
        
        return tx_service

    def run_service(self, service: Any, params: Dict[str, Any]) -> None:
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
        
        ### CAMBIO: El builder ya no dirige el flujo, solo lo inicia llamando a 'run' ###
        service.run(form_data=datos, path=path_fichero, filename=filename)
        
        log.info(f"Proceso de {config.TRANSACTION_CODE} completado.")