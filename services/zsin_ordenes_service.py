# Fichero: services/zsin_ordenes_service.py

import logging
from pathlib import Path
from typing import Optional, Protocol

# ## XXX CAMBIO 1: Se eliminan las importaciones de la configuración antigua.
# Se añaden los tipos necesarios para la Inyección de Dependencias.
from config.settings import TransactionConfig
from core.builders.sap_payload_builder import SapPayloadBuilder
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
    Ahora recibe todas sus dependencias en el constructor.
    """
    # ## XXX CAMBIO 2: El constructor se actualiza para recibir 'config' y 'payload_builder'.
    def __init__(
        self,
        transaction_service: TransactionService,
        page: ZsinOrdenesPage,
        config: TransactionConfig,
        payload_builder: SapPayloadBuilder,
        file_handler: Optional[FileHandlerProtocol] = None,
        print_service: Optional[PrintServiceProtocol] = None,
    ):
        self._transaction_service = transaction_service
        self._page = page
        self.config = config  # Inyectado
        self._payload_builder = payload_builder  # Inyectado
        self._file_handler = file_handler
        self._print_service = print_service
        # La línea 'self._config = ZsinOrdenesConfig()' se ha eliminado.

    def run(self, criteria: ZsinOrdenesCriteria, options: ZsinOrdenesExecutionOptions):
        """
        Orquesta el flujo completo de la transacción ZSIN_ORDENES.
        """
        try:
            # ## XXX CAMBIO 3: Se usa la configuración inyectada.
            self._transaction_service.run_transaction(self.config.transaction_code)

            # TODO FIXME DEBUG self._page.pause()

            # ## XXX CAMBIO 4: Se usa la INSTANCIA del payload_builder inyectado.
            payload = self._payload_builder.build_payload(criteria)

            self._page.rellenar_formulario(payload)
            self._page.ejecutar()
            total = self._page.obtener_resultados()

            # TODO FIXME DEBUG self._page.pause()

            if total < 1:
                log.warning("No se encontraron resultados para los criterios de búsqueda.")
                return
            log.info(f"✅ Se encontraron {total} resultados.")

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