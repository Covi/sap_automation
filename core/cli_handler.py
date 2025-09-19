# core/cli_handler.py

import argparse
import logging
import sys
from dataclasses import dataclass, fields
from typing import Dict, Any, Optional

from core.registry import TRANSACTION_REGISTRY
from config import DEFAULT_BROWSER

log = logging.getLogger(__name__)

@dataclass
class RunConfig:
    """Contiene todos los datos necesarios para ejecutar una transacción."""
    transaction_name: str
    params: Dict[str, Any]
    browser: str
    headless: bool
    log_level: Optional[str]
    download_dir: Optional[str]
    persistent_session: bool = False  # <--- AÑADE ESTA LÍNEA

class CliHandler:
    def __init__(self):
        self.available_trxs = list(TRANSACTION_REGISTRY.keys())
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Crea y configura el parser de argumentos."""
        parser = argparse.ArgumentParser(
            description="Automatización SAP Web GUI",
            formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument("transaccion", nargs='?', default=None, help="Nombre de la transacción a ejecutar.")
        parser.add_argument("params", nargs='*', help="Parámetros 'clave=valor' para la transacción.")
        parser.add_argument(
            '-i', '--info', 
            action='store_true', 
            help="Muestra los parámetros disponibles para una transacción y sale."
        )
        parser.add_argument("-l", "--list", action='store_true', help="Lista las transacciones disponibles y sale.")
        parser.add_argument('-b', '--browser', type=str, choices=['firefox', 'chromium', 'webkit'], default=DEFAULT_BROWSER, help=f"Navegador a usar (defecto: {DEFAULT_BROWSER}).")
        parser.add_argument('-hd', '--headless', action='store_true', help="Ejecuta el navegador en modo headless (sin UI).")
        parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Establece el nivel de log.")
        parser.add_argument('-y', '--yes', action='store_true', help="Asume 'sí' en todas las preguntas de confirmación.")
        parser.add_argument('-u', '--unattended', action='store_true', help="Modo desatendido para servicios. Exige nombres exactos.")
        parser.add_argument('--download-dir', type=str, help="Sobrescribe el directorio de descarga por defecto.")
        parser.add_argument(
            "-p",
            "--persistent",
            action="store_true",  # <--- Esto hace que si el flag está, el valor sea True
            help="Activa la estrategia de persistencia para mantener el navegador abierto."
        )

        return parser

    def _parse_params(self, param_list: list[str]) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        for p in param_list:
            if '=' in p: k, v = p.split('=', 1); params[k] = v
            else: params[p] = True
        return params

    def list_transactions(self):
        print("\nTransacciones disponibles:"); [print(f"  - {trx}") for trx in self.available_trxs]; print()

    def show_transaction_info(self, trx_name: str):
        """Inspecciona y muestra los parámetros del formulario y de configuración."""
        
        trx_name = trx_name.lower()
        if trx_name not in self.available_trxs:
            log.error(f"Transacción '{trx_name}' no encontrada.")
            return

        recipe = TRANSACTION_REGISTRY[trx_name]

        # --- 1. Parámetros del Formulario (Pydantic Schemas) ---
        print(f"\nParámetros del Formulario para '{trx_name}':")

        # Procesa el schema de criterios, que siempre está presente
        criteria_schema = recipe.criteria_schema
        print("  --- Criterios ---")
        for name, info in criteria_schema.model_fields.items():
            if info.is_required():
                print(f"    - {name} (Obligatorio)")
            else:
                print(f"    - {name} (Opcional, por defecto: {info.default})")

        # Procesa el schema de opciones, solo si la transacción lo define
        if recipe.options_schema:
            options_schema = recipe.options_schema
            print("\n  --- Opciones ---")
            for name, info in options_schema.model_fields.items():
                if info.is_required():
                    print(f"    - {name} (Obligatorio)")
                else:
                    print(f"    - {name} (Opcional, por defecto: {info.default})")

        # --- 2. Parámetros de Configuración (dataclasses fields) ---
        config_class = recipe.config_class
        config_instance = config_class()

        print(f"\nParámetros de Configuración para '{trx_name}':")

        for field in fields(config_class):
            if field.metadata.get('sensitive'):
                print(f"    - {field.name} (Valor: '********')")
            else:
                current_value = getattr(config_instance, field.name)
                print(f"    - {field.name} (Valor por defecto: '{current_value}')")

        print()

    def resolve_transaction_name(self, name_input: str, unattended: bool, assume_yes: bool) -> Optional[str]:
        """Resuelve el nombre de la transacción según el modo de ejecución."""
        if name_input.lower() in self.available_trxs:
            return name_input.lower()

        if unattended:
            log.error(f"Modo desatendido: Se requiere un nombre exacto. '{name_input}' no es válido.")
            return None
        
        possible_matches = [trx for trx in self.available_trxs if trx.startswith(name_input.lower())]

        if len(possible_matches) == 1:
            resolved_name = possible_matches[0]
            if assume_yes:
                log.info(f"Coincidencia única para '{name_input}': '{resolved_name}'. Asumiendo 'sí'.")
                return resolved_name
            
            try:
                sys.stdout.write(f"¿Quisiste decir '{resolved_name}'? [S/n]: ")
                sys.stdout.flush()
                confirm = sys.stdin.readline().strip()
                return resolved_name if confirm.lower() in ('s', 'si', '') else None
            except (KeyboardInterrupt, EOFError):
                sys.stdout.write("\n"); log.warning("Operación cancelada."); return None
        
        elif len(possible_matches) > 1:
            log.warning(f"'{name_input}' es ambiguo. Coincide con: {', '.join(possible_matches)}")
        else:
            log.error(f"No se encontró ninguna transacción que coincida con '{name_input}'.")
        
        return None

    def handle_request(self) -> Optional[RunConfig]:
        """Parsea argumentos y devuelve la configuración de ejecución o None."""
        args = self.parser.parse_args()

        if args.list:
            self.list_transactions()
            return None
            
        if args.info:
            if not args.transaccion:
                log.error("Debes especificar una transacción para ver su información (ej: main.py mb52 --info).")
            else:
                self.show_transaction_info(args.transaccion)
            return None

        if not args.transaccion:
            log.warning("No se especificó una transacción."); self.parser.print_help(); return None

        resolved_trx_name = self.resolve_transaction_name(
            args.transaccion,
            unattended=args.unattended,
            assume_yes=args.yes
        )

        if not resolved_trx_name:
            return None

        return RunConfig(
            transaction_name=resolved_trx_name,
            params=self._parse_params(args.params),
            browser=args.browser,
            headless=args.headless,
            log_level=args.log_level, 
            download_dir=args.download_dir, 
            persistent_session=args.persistent
        )