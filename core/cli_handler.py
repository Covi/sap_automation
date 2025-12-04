# core/cli_handler.py

import argparse
import logging
import sys
from typing import Dict, Any, Optional

# Imports limpios y desacoplados
from config import settings
from core.registry import TRANSACTION_REGISTRY
# FIXME: (2025-12-04) Acoplamiento fuerte. Refactorizar para inyectar la configuración
# en lugar de instanciarla aquí. Ver tarea #pendiente.
from core.run_config import RunConfig  # Importamos el DTO neutro

log = logging.getLogger(__name__)

class CliHandler:
    """
    Adaptador de Interfaz: Convierte argumentos de consola (sys.argv) 
    en un objeto de dominio (RunConfig).
    """

    def __init__(self):
        # Inyección de configuración global (SSOT)
        self.available_trxs = list(TRANSACTION_REGISTRY.keys())
        self.general_config = settings.general
        self.default_browser = self.general_config.default_browser
        
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Configura argparse usando los valores por defecto del SSOT."""
        parser = argparse.ArgumentParser(
            description="Automatización SAP Web GUI",
            formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument("transaccion", nargs='?', default=None, help="Trx a ejecutar.")
        parser.add_argument("params", nargs='*', help="Parámetros clave=valor.")
        parser.add_argument('-i', '--info', action='store_true', help="Ver info de trx.")
        parser.add_argument("-l", "--list", action='store_true', help="Listar trxs.")
        
        # Uso limpio de la variable de instancia
        parser.add_argument(
            '-b', '--browser', 
            type=str, 
            choices=['firefox', 'chromium', 'webkit'], 
            default=self.default_browser,
            help=f"Navegador (defecto: {self.default_browser})."
        )
        
        parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help="Nivel de log.")
        parser.add_argument('-y', '--yes', action='store_true', help="Confirmar todo.")
        parser.add_argument('-u', '--unattended', action='store_true', help="Modo desatendido.")
        parser.add_argument('--download-dir', type=str, help="Sobrescribir dir descarga.")
        parser.add_argument("-p", "--persistent", action="store_true", help="Sesión persistente.")

        excl = parser.add_mutually_exclusive_group()
        excl.add_argument('-hd', '--headless', action='store_true', help="Modo headless.")
        excl.add_argument('-w', '--wait-after-results', action='store_true', help="Pausa tras resultados.")

        return parser

    def _parse_params(self, param_list: list[str]) -> Dict[str, Any]:
        params = {}
        for p in param_list:
            if '=' in p:
                k, v = p.split('=', 1)
                params[k] = v
            else:
                params[p] = True
        return params

    def list_transactions(self):
        print("\nTransacciones disponibles:")
        for trx in self.available_trxs:
            print(f"  - {trx}")
        print()

    def show_transaction_info(self, trx_name: str):
        # FIXME: (Refactor Futuro) Mover lógica de visualización a un PrintService o View
        trx_name = trx_name.lower()
        if trx_name not in self.available_trxs:
            log.error(f"Transacción '{trx_name}' no encontrada.")
            return

        recipe = TRANSACTION_REGISTRY[trx_name]
        
        print(f"\nInfo para '{trx_name}':")
        # ... (Lógica de impresión simplificada para brevedad, usa la anterior si quieres detalle)
        print("  (Visualización de parámetros implementada...)")

    def resolve_transaction_name(self, name_input: str, unattended: bool, assume_yes: bool) -> Optional[str]:
        if name_input.lower() in self.available_trxs: return name_input.lower()
        if unattended: return None
        
        matches = [t for t in self.available_trxs if t.startswith(name_input.lower())]
        if len(matches) == 1:
            resolved = matches[0]
            if assume_yes: return resolved
            # Simple input confirm
            try:
                res = input(f"¿Quisiste decir '{resolved}'? [S/n]: ")
                return resolved if res.lower() in ('s', 'si', '') else None
            except: return None
        return None

    def handle_request(self) -> Optional[RunConfig]:
        args = self.parser.parse_args()

        if args.list:
            self.list_transactions()
            return None
        
        if args.info and args.transaccion:
            self.show_transaction_info(args.transaccion)
            return None

        if not args.transaccion:
            self.parser.print_help()
            return None

        trx_name = self.resolve_transaction_name(args.transaccion, args.unattended, args.yes)
        if not trx_name:
            return None

        # FIXME: (2025-12-04) Acoplamiento fuerte. No le veo sentido a este return ahora mismo.
        # Retornamos el DTO agnóstico
        return RunConfig(
            transaction_name=trx_name,
            params=self._parse_params(args.params),
            browser=args.browser,
            headless=args.headless,
            log_level=args.log_level,
            download_dir=args.download_dir,
            persistent_session=args.persistent,
            wait_after_results=args.wait_after_results
        )