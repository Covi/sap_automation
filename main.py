# main.py (VERSIÓN FINAL Y CORRECTA)

import logging, os, sys
from core.logging.logger_config import setup_logging
from core.cli_handler import CliHandler
from config import BaseConfig, BASE_URL

# --- Abstracciones y Estrategias ---
from core.protocols.closing_strategy_protocol import ClosingStrategy
from core.strategies.browser_closing_strategies import TransientClosingStrategy, PersistentClosingStrategy

# --- Implementaciones Concretas ---
from core.factories.playwright_browser_factory import PlaywrightBrowserFactory
from core.browser_manager import BrowserManager

# --- Lógica de la Aplicación (Páginas y Servicios) ---
from pages.sap_login_page import SAPLoginPage
from pages.sap_easy_access_page import SAPEasyAccessPage
from services.login_service import LoginService
from services.session_service import SessionService
from core.builders.generic_transaction_builder import GenericTransactionBuilder
from core.providers.locator_provider_factory import LocatorProviderFactory

# Configuración del Logger
log = logging.getLogger(__name__)

# Archivo para guardar el estado de la sesión
STATE_FILE = "auth_state.json"

def main() -> None:
    """
    Orquesta la ejecución de la aplicación, componiendo todas las dependencias
    y ejecutando el flujo de negocio.
    """
    handler = CliHandler()
    run_config = handler.handle_request()

    if not run_config:
        return

    setup_logging(log_level=run_config.log_level)
    log.info(f"Iniciando transacción '{run_config.transaction_name}'...")

    # ======================================================================
    # PASO 1: COMPOSICIÓN DE DEPENDENCIAS (El Corazón de SOLID)
    # ======================================================================

    # Elegimos la estrategia de cierre basada en la configuración
    # Esto resuelve tu FIXME y hace la intención explícita.
    closing_strategy: ClosingStrategy
    if run_config.persistent_session: # Asumiendo que tu run_config tiene este flag
        closing_strategy = PersistentClosingStrategy()
        log.info("Usando Estrategia de Cierre Persistente.")
    else:
        closing_strategy = TransientClosingStrategy()
        log.info("Usando Estrategia de Cierre Transitoria.")

    # Creamos las implementaciones concretas
    factory = PlaywrightBrowserFactory(browser_type=run_config.browser)
    manager = BrowserManager(
        factory=factory,
        closing_strategy=closing_strategy,
        headless=run_config.headless
    )

    # ======================================================================
    # PASO 2: EJECUCIÓN DE LA LÓGICA
    # ======================================================================
    try:
        page = manager.start_browser_with_session( # Usamos el método correcto
            storage_state_path=STATE_FILE if os.path.exists(STATE_FILE) else None
        )
        page.goto(BASE_URL)

        # --- Composición de la capa de aplicación ---
        locator_factory = LocatorProviderFactory()
        login_page = SAPLoginPage(page, locator_factory.create("login.toml"))
        easy_access_page = SAPEasyAccessPage(page, locator_factory.create("easy_access.toml"))

        login_service = LoginService(login_page, easy_access_page)
        session_service = SessionService(easy_access_page)

        # --- Flujo de negocio de alto nivel ---
        if not session_service.is_session_active():
            log.warning("No se ha detectado sesión activa. Procediendo con el login...")
            credentials = BaseConfig()
            login_service.login(user=credentials.SAP_USERNAME, pss=credentials.SAP_PASSWORD)
            manager.save_session(STATE_FILE)
        else:
            log.info("Sesión recuperada con éxito desde el fichero de estado.")
        
        # --- Transacción ---
        builder = GenericTransactionBuilder(run_config.transaction_name)
        transaction_service = builder.build_service(page)
        builder.run_service(transaction_service, run_config.params)

    except Exception as e:
        log.error(f"Error fatal en la ejecución: {e}", exc_info=True)
        sys.exit(1) # Salida con código de error
    finally:
        log.info("Ejecutando estrategia de cierre del navegador.")
        # --- El cierre SIEMPRE se llama. La estrategia decide qué hacer. ---
        manager.close_browser()

if __name__ == "__main__":
    main()