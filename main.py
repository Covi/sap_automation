# Fichero: main.py

import logging
from pathlib import Path

# Importamos la config y las "fuentes de verdad"
from config.settings import (
    general_config,
    log_config, 
    env_settings,
    TRANSACTION_CONFIGS
)
from core.registry import TRANSACTION_REGISTRY
DEFAULT_BROWSER = general_config.default_browser

from core.builders.generic_transaction_builder import GenericTransactionBuilder
from core.browser_manager import BrowserManager
from core.cli_handler import CliHandler
from core.logging.logger_config import setup_logging
from core.providers.locator_provider_factory import LocatorProviderFactory
from core.providers.locators.toml_locator_provider import TomlLocatorProvider

# --- Importaciones de la librería de autenticación ---
from covi_auth_lib import LoginService, PlaywrightAdapter, UsernamePasswordProvider

log = logging.getLogger(__name__)

def main() -> None:
    """Orquesta la ejecución de la aplicación, actuando como la Raíz de Composición."""
    handler = CliHandler(DEFAULT_BROWSER, TRANSACTION_REGISTRY)
    run_config = handler.handle_request()

    if not run_config:
        log.info("Operación finalizada sin ejecutar transacción.")
        return

    setup_logging(log_config)
    log.info(f"Iniciando transacción '{run_config.transaction_name}'...")

    # XXX Se cargan las dependencias principales una sola vez al inicio.
    # Estas son las únicas implementaciones concretas que 'main' conocerá.
    registry = TRANSACTION_REGISTRY
    configs = TRANSACTION_CONFIGS

    # --- Fábrica agnóstica de locators ---
    # XXX Creamos los providers inyectando los ficheros concretos y comunes
    common_provider = TomlLocatorProvider(Path("config/locators/common.toml"))
    locator_factory = LocatorProviderFactory(common_providers=[common_provider])

    # XXX Se inyectan las dependencias en el builder.
    # El builder ya no importa sus dependencias; las recibe.
    builder = GenericTransactionBuilder(
        registry=registry,
        configs=configs,
        provider_factory=locator_factory
    )

    manager = BrowserManager(
        browser_type=run_config.browser,
        headless=run_config.headless
    )
    page = manager.start_browser()

    try:
        # --- NAVEGACIÓN INICIAL ---
        # XXX Usamos el objeto de configuración importado.
        log.info(f"Navegando a la URL de SAP: {general_config.base_url}")
        page.goto(general_config.base_url)

        # --- FLUJO DE LOGIN ---
        # XXX Provider específico de login
        login_specific = TomlLocatorProvider(Path("config/locators/login.toml"))
        login_provider = locator_factory.create(login_specific)

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

        # XXX Las credenciales se obtienen del objeto 'env_settings'.
        # Ya no se instancia 'BaseConfig'.
        if not login_service.login(user=env_settings.sap_username, password=env_settings.sap_password):
            raise RuntimeError("El proceso de login ha fallado. Abortando transacción.")

        log.info("Login realizado con éxito.")

        # --- EJECUCIÓN DE LA TRANSACCIÓN ---
        # XXX Se usan los nuevos métodos del builder "puro".
        # El código de la transacción se pasa como parámetro, ya no es estado interno.
        service = builder.build_service(run_config.transaction_name, page)
        builder.run_service(service, run_config.transaction_name, run_config.params)

    except (ValueError, KeyError) as e:
        log.error(f"Error de configuración o parámetros: {e}", exc_info=True)
    except Exception as e:
        log.error(f"Error inesperado ejecutando la transacción '{run_config.transaction_name}': {e}", exc_info=True)
    finally:
        log.info("Cerrando el navegador.")
        manager.close_browser()


if __name__ == "__main__":
    main()
