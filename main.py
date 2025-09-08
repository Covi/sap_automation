# main.py
import argparse

# Logging
import logging
log = logging.getLogger(__name__)

from typing import Dict, Any
from core.browser_manager import BrowserManager
from core.builders.generic_transaction_builder import GenericTransactionBuilder
from core.logging.logger_config import setup_logging
from config import DEFAULT_BROWSER

def parse_params(param_list: list[str]) -> Dict[str, Any]:
    """Convierte una lista de 'k=v' en un diccionario."""
    params: Dict[str, Any] = {}
    for p in param_list:
        if '=' in p:
            k, v = p.split('=', 1)
            params[k] = v
        else:
            params[p] = True
    return params

def main() -> None:
    parser = argparse.ArgumentParser(description="Automatización SAP Web GUI")
    parser.add_argument("transaccion", type=str, help="Nombre de la transacción a ejecutar (ej: mb52)")
    parser.add_argument("params", nargs='*', help="Parámetros 'clave=valor' para la transacción")
    parser.add_argument(
        '-b', '--browser',
        type=str,
        choices=['firefox', 'chromium', 'webkit'],
        help=f"Navegador a usar. Por defecto: {DEFAULT_BROWSER}"
    )
    parser.add_argument(
        '-hd', '--headless',
        action='store_true',
        help="Ejecuta el navegador en modo headless (sin interfaz gráfica)."
    )
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Nivel de log (por defecto: el definido en config)."
    )

    args = parser.parse_args()
    params = parse_params(args.params)

    # --- Inicializamos logging ---
    setup_logging(log_level=args.log_level)  # usa CLI si se da, config si no
    log.info("Iniciando ejecución de transacción...")

    # Decide navegador: argumento > config
    browser_type = args.browser or DEFAULT_BROWSER

    manager = BrowserManager(browser_type=browser_type, headless=args.headless)
    page = manager.start_browser()

    try:
        builder = GenericTransactionBuilder(args.transaccion.lower())
        service = builder.build_service(page)
        builder.run_service(service, params)
    except (ValueError, KeyError) as e:
        log.error(f"Error de configuración o parámetros: {e}", exc_info=True)
    except Exception as e:
        log.error(f"Error inesperado ejecutando la transacción '{args.transaccion}': {e}", exc_info=True)
    finally:
        log.info("Cerrando el navegador.")
        manager.close_browser()

if __name__ == "__main__":
    main()
