# main.py

# Logging
import logging
log = logging.getLogger(__name__)

from core.browser_manager import BrowserManager
from core.builders.generic_transaction_builder import GenericTransactionBuilder
from core.logging.logger_config import setup_logging
from core.cli_handler import CliHandler

def main() -> None:
    """Orquesta la ejecución de la aplicación."""
    
    # 1. Delega toda la lógica de CLI al handler
    handler = CliHandler()
    run_config = handler.handle_request()

    # 2. Si el handler devuelve None, la operación ya terminó (ej: --list) o fue cancelada.
    if not run_config:
        log.info("Operación finalizada sin ejecutar transacción.")
        return

    # 3. Si hay configuración, se procede con la ejecución.
    setup_logging(log_level=run_config.log_level)
    log.info(f"Iniciando transacción '{run_config.transaction_name}'...")

    manager = BrowserManager(
        browser_type=run_config.browser, 
        headless=run_config.headless
    )
    page = manager.start_browser()

    try:
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