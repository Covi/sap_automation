# services/zsin_ordenes_service.py

import logging
from pathlib import Path
from typing import Optional, Protocol

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

    # --- La firma y la lógica del método 'run' se actualizan ---
    def run(self, criteria: ZsinOrdenesCriteria, options: ZsinOrdenesExecutionOptions):
        """
        Orquesta el flujo completo de la transacción ZSIN_ORDENES.

        :param criteria: Criterios de búsqueda para el formulario.
        :param options: Opciones de ejecución (acciones, configuración de salida).
        """
        try:
            self._transaction_service.run_transaction(self._config.TRANSACTION_CODE)

            # Modelo
            payload = SapPayloadBuilder.build_payload(criteria)

            self._page.rellenar_formulario(payload)
            self._page.ejecutar()
            total = self._page.obtener_resultados()

            if total < 1:
                log.warning("No se encontraron resultados para los criterios de búsqueda.")
                return
            log.info(f"✅ Se encontraron {total} resultados.")

            log.debug(f"[SERVICE] options.wait_after_results = {options.wait_after_results}")
            # Espera manual tras resultados si está configurada
            if getattr(options, "wait_after_results", False):
                log.info("Pausa manual tras obtener resultados (solo modo UI).")
                self._page.pause()

            self._page.pause()
            self._page.seleccionar_todas_las_ordenes()
            self._page.pause()

            # --- OPTIONS ---
            if options.reenviar:
                log.info("Acción: Reenviar órdenes.")
                self._page.seleccionar_todas_las_ordenes()
                self._page.reenviar_ordenes()

            if options.imprimir:
                if not (self._file_handler and self._print_service):
                    log.warning("No se inyectaron dependencias de archivo/impresión. Se omite paso de impresión.")
                    return

                log.info("Acción: Imprimir órdenes.")
                self._page.seleccionar_todas_las_ordenes()

                filename = options.output_filename
                path = options.output_path

                log.debug(f"Esperando fichero de descarga que contenga: '{filename}'")
                pdf_bytes = self._page.descargar_pdf(filename)
                pdf_path = self._file_handler.save_with_timestamp(pdf_bytes, path, filename)
                log.debug(f"✅ PDF guardado con éxito en: {pdf_path.resolve()}")

                self._print_service.imprimir_fichero(pdf_path)

        except Exception as e:
            log.error(f"Error en ZSIN_ORDENES: {e}", exc_info=True)
            raise