# main.py

import argparse
import importlib
from typing import Dict, Any
from core.browser_manager import BrowserManager
from utils.logger import log
from core.builders.builder_protocol import BuilderProtocol

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
    parser.add_argument("transaccion", type=str, help="Nombre de la transacción a ejecutar")
    parser.add_argument('params', nargs='*', help='Parámetros clave=valor para la transacción')
    args = parser.parse_args()

    params = parse_params(args.params)

    manager = BrowserManager(headless=True)
    page = manager.start_browser()

    try:
        module = importlib.import_module(f"core.builders.{args.transaccion.lower()}_builder")
        builder: BuilderProtocol = getattr(module, "builder")

        service = builder.build_service(page)
        builder.run_service(service, params)

    except Exception as e:
        log.error(f"Error ejecutando transacción {args.transaccion}: {e}", exc_info=True)
    finally:
        manager.close_browser()

if __name__ == "__main__":
    main()