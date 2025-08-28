import argparse
from typing import Dict, Any
from config import BROWSER
from core.browser_manager import BrowserManager
from core.builders.generic_builder import GenericTransactionBuilder
from utils.logger import log
from infra.playwright_browser_factory import PlaywrightBrowserFactory

def parse_params(param_list: list[str]) -> Dict[str, Any]:
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
    parser.add_argument('params', nargs='*', help="Parámetros 'clave=valor' para la transacción")
    parser.add_argument('-hd', '--headless', action='store_true', help="Ejecuta en modo headless")

    args = parser.parse_args()
    params = parse_params(args.params)

    # 🟢 main ya no conoce Playwright, solo la factoría
    factory = PlaywrightBrowserFactory(browser_type=BROWSER, headless=args.headless)
    manager = BrowserManager(factory)
    page = manager.start_browser()

    try:
        builder = GenericTransactionBuilder(args.transaccion.lower())
        service = builder.build_service(page)
        builder.run_service(service, params)
    except Exception as e:
        log.error(f"Error inesperado: {e}", exc_info=True)
    finally:
        log.info("Cerrando el navegador.")
        manager.close_browser()

if __name__ == "__main__":
    main()
