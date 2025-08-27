# Fichero: main.py

import argparse
from typing import Dict, Any, List
from core.browser_manager import BrowserManager
from utils.logger import log
from core.builders.generic_builder import GenericTransactionBuilder


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
    args = parser.parse_args()

    params = parse_params(args.params)
    manager = BrowserManager(headless=True)
    page = manager.start_browser()

    try:
        # La lógica ahora es mucho más directa:
        # 1. Se crea el builder para la transacción solicitada.
        builder = GenericTransactionBuilder(args.transaccion.lower())
        
        # 2. Se construye el servicio.
        service = builder.build_service(page)
        
        # 3. Se ejecuta con los parámetros.
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