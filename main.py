# main.py

import logging
from core.browser_manager import BrowserManager
from core.builders.generic_transaction_builder import GenericTransactionBuilder
from core.logging.logger_config import setup_logging
from core.cli_handler import CliHandler
from core.providers.locator_provider_factory import LocatorProviderFactory
from core.registry import TRANSACTION_REGISTRY
from config import SAP_BASE_URL

# --- IMPORTACIONES DE TU NUEVA LIBRERÍA ---
from covi_auth_lib import LoginService, PlaywrightAdapter, UsernamePasswordProvider

log = logging.getLogger(__name__)

def main() -> None:
    """Orquesta la ejecución de la aplicación."""
    handler = CliHandler()
    run_config = handler.handle_request()

    if not run_config:
        log.info("Operación finalizada sin ejecutar transacción.")
        return

    setup_logging(log_level=run_config.log_level)
    log.info(f"Iniciando transacción '{run_config.transaction_name}'...")

    manager = BrowserManager(
        browser_type=run_config.browser, 
        headless=run_config.headless
    )
    page = manager.start_browser()
    
    try:
        log.info(f"Navegando a la URL de SAP: {SAP_BASE_URL}")
        page.goto(SAP_BASE_URL)

        # --- Obtener la config concreta ANTES del login ---
        recipe = TRANSACTION_REGISTRY[run_config.transaction_name]
        config = recipe.config_class()

        # --- FLUJO DE LOGIN ---
        factory = LocatorProviderFactory()
        login_provider = factory.create("login.toml")
        
        user_selector = login_provider.get("form.input_user")
        password_selector = login_provider.get("form.input_password")
        submit_selector = login_provider.get("form.input_login")

        adapter = PlaywrightAdapter(page)
        auth_provider = UsernamePasswordProvider(
            ui_adapter=adapter,
            user_selector=user_selector,
            password_selector=password_selector,
            submit_selector=submit_selector
        )
        login_service = LoginService(provider=auth_provider)
        
        if not login_service.login(user=config.SAP_USERNAME, password=config.SAP_PASSWORD):
            raise RuntimeError("El proceso de login ha fallado. Abortando transacción.")
        
        log.info("Login realizado con éxito.")
        
        # --- FLUJO DE TRANSACCIÓN ---
        builder = GenericTransactionBuilder(run_config.transaction_name)
        service = builder.build_service(page)
        builder.run_service(service, run_config.params)

    except (ValueError, KeyError) as e:
        log.error(f"Error de configuración o parámetros: {e}", exc_info=True)
    except Exception as e:
        log.error(f"Error inesperado ejecutando la transacción '{run_config.transaction_name}': {e}", exc_info=True)
    finally:
        log.info("Cerrando el navegador.")
        manager.close_browser()

if __name__ == "__main__":
    main()
