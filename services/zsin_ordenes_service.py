# services/zsin_ordenes_service.py

import logging
from pathlib import Path
from typing import Callable, Dict, Optional, Protocol

from config import ZsinOrdenesConfig
from core.builders.sap_payload_builder import SapPayloadBuilder

# --- CAMBIO CLAVE: Importación actualizada a la nueva ruta y nombres ---
from schemas.zsin_ordenes import ZsinOrdenesCriteria, ZsinOrdenesExecutionOptions
from services.transaction_service import TransactionService
from pages.zsin_ordenes_page import ZsinOrdenesPage

log = logging.getLogger(__name__)

# --- Protocolos para dependencias externas (sin cambios) ---
class FileHandlerProtocol(Protocol):
    def save_with_timestamp(self, data: bytes, path: Path, filename: str) -> Path: ...

class PrintServiceProtocol(Protocol):
    def imprimir_fichero(self, ruta_fichero: Path) -> None: ...

class EnvioOrdenesService:
    def __init__(self, page: ZsinOrdenesPage, logger: logging.Logger):
        self._page = page
        self._log = logger

    def ejecutar(self):
        self._log.info("Acción: Reenviar órdenes.")
        self._page.seleccionar_todas_las_ordenes()
        self._page.reenviar_ordenes()
        self._log.info("✅ Reenvío completado correctamente.")

class ImpresionOrdenesService:
    def __init__(self, page, file_handler, print_service, logger):
        self._page = page
        self._file_handler = file_handler
        self._print_service = print_service
        self._log = logger

    def ejecutar(self, filename: str, path: Path):
        self._log.info("Acción: Imprimir órdenes.")
        self._page.seleccionar_todas_las_ordenes()

        self._log.debug(f"Esperando fichero de descarga que contenga: '{filename}'")
        pdf_bytes = self._page.descargar_pdf(filename)
        pdf_path = self._file_handler.save_with_timestamp(pdf_bytes, path, filename)
        self._log.debug(f"✅ PDF guardado con éxito en: {pdf_path.resolve()}")

        self._print_service.imprimir_fichero(pdf_path)
        self._log.info("✅ Impresión completada correctamente.")


class ZsinOrdenesService:
    """
    Servicio para la transacción ZSIN_ORDENES.

    :param transaction_service: Servicio genérico de transacciones SAP.
    :param page: Página de la transacción ZSIN_ORDENES.
    :param file_handler: Servicio opcional para manejo de ficheros.
    :param print_service: Servicio opcional para impresión.
    """
    def __init__(
        self,
        transaction_service: TransactionService,
        page: ZsinOrdenesPage,
        file_handler: Optional[FileHandlerProtocol] = None,
        print_service: Optional[PrintServiceProtocol] = None,
    ):
        self._transaction_service = transaction_service
        self._page = page
        self._config = ZsinOrdenesConfig()
        self._file_handler = file_handler
        self._print_service = print_service

        # Inyección de subservicios especializados
        self._impresion = None
        self._envio = None

        if file_handler and print_service:
            self._impresion = ImpresionOrdenesService(page, file_handler, print_service, log)
        self._envio = EnvioOrdenesService(page, log)

    def _ejecutar_seguro(self, funcion: Callable, nombre_accion: str) -> Dict[str, str]:
        """
        Ejecuta una acción y captura posibles errores, devolviendo un dict con estado.
        """
        try:
            funcion()
            log.info(f"{nombre_accion} completada con éxito.")
            return {"status": "ok"}
        except Exception as e:
            log.error(f"Error en {nombre_accion}: {e}", exc_info=True)
            return {"status": "error", "error": str(e)} 

    # --- La firma y la lógica del método 'run' se actualizan ---
    def run(self, criteria: ZsinOrdenesCriteria, options: ZsinOrdenesExecutionOptions):
        """
        Orquesta el flujo completo de la transacción ZSIN_ORDENES.

        :param criteria: Criterios de búsqueda para el formulario.
        :param options: Opciones de ejecución (acciones, configuración de salida).
        """
        try:
            resultados: Dict[str, Dict[str, str]] = {}

            self._transaction_service.run_transaction(self._config.TRANSACTION_CODE)

            # Modelo
            payload = SapPayloadBuilder.build_payload(criteria)
            # Recuperar la espera del formulario antes de rellenarlo
            self._page.esperar_formulario()
            self._page.rellenar_formulario(payload)
            self._page.ejecutar()
            self._page.esperar_resultados(60000)

            # --- Resultados ---
            total = self._page.obtener_resultados()

            if total < 1:
                log.warning("No se encontraron resultados para los criterios de búsqueda.")
                return
            log.info(f"✅ Se encontraron {total} resultados.")

            # --- Opciones ---
            if options.reenviar and self._envio:
                resultados["envio"] = self._ejecutar_seguro(
                    self._envio.ejecutar,
                    "Reenvío"
                )

            if options.imprimir and self._impresion:
                resultados["impresion"] = self._ejecutar_seguro(
                    lambda: self._impresion.ejecutar(
                        options.output_filename, options.output_path
                    ),
                    "Impresión"
                )

            # --- Fin ---
            # Espera manual tras resultados si está configurada
            # No hace falta getattr porque wait_after_results es pydantic y está en ZsinOrdenesExecutionOptions
            if options.wait_after_results:
                log.info("Pausa manual tras obtener resultados (solo modo UI).")
                self._page.pause()

            return resultados

        except Exception as e:
            log.error(f"Error en ZSIN_ORDENES: {e}", exc_info=True)
            raise