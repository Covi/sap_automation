# services/zsin_ordenes_service.py

import logging
from pathlib import Path
from typing import Optional, Protocol

from config import ZsinOrdenesConfig
from core.builders.sap_payload_builder import SapPayloadBuilder

from data_models.zsin_ordenes_models import ZsinOrdenesFormData
from services.transaction_service import TransactionService
from pages.zsin_ordenes_page import ZsinOrdenesPage

log = logging.getLogger(__name__)

# --- Protocols para dependencias externas ---
class FileHandlerProtocol(Protocol):
    def save_with_timestamp(self, data: bytes, path: Path, filename: str) -> Path: ...

class PrintServiceProtocol(Protocol):
    def imprimir_fichero(self, ruta_fichero: Path) -> None: ...

class ZsinOrdenesService:
    def __init__(
        self,
        transaction_service: TransactionService,
        page: ZsinOrdenesPage,
        file_handler: Optional[FileHandlerProtocol] = None,
        print_service: Optional[PrintServiceProtocol] = None,
    ):
        """
        Servicio para la transacción ZSIN_ORDENES.

        :param transaction_service: Servicio genérico de transacciones SAP.
        :param page: Página de la transacción ZSIN_ORDENES.
        :param file_handler: Servicio opcional para manejo de ficheros.
        :param print_service: Servicio opcional para impresión.
        """
        self._transaction_service = transaction_service
        self._page = page
        self._config = ZsinOrdenesConfig()
        self._file_handler = file_handler
        self._print_service = print_service

    def run(self, form_data: ZsinOrdenesFormData, path: Path, filename: str):
        """
        Orquesta el flujo completo de la transacción ZSIN_ORDENES.

        :param form_data: Datos del formulario a enviar.
        :param path: Directorio donde guardar ficheros descargados.
        :param filename: Nombre del fichero a generar.
        """
        try:
            # 1. Entrar en la transacción
            self._transaction_service.run_transaction(self._config.TRANSACTION_CODE)

            # 2. Construir payload a partir del formulario
            payload = SapPayloadBuilder.build_payload(form_data)

            # 3. Rellenar formulario en la página
            self._page.rellenar_formulario(payload)

            # 4. Ejecutar búsqueda y obtener resultados
            self._page.ejecutar_busqueda()
            total = self._page.obtener_resultados()
            if total < 1:
                log.warning("No se encontraron resultados para los criterios de búsqueda.")
                return
            log.info(f"✅ Se encontraron {total} resultados.")

            # FIXME esto no es semánticamente correcto porque esto no es form data, pero es que el payload, 
            # el modelo ni siquiera debería ser form data sino simplemente data model
            # self._page.pause()

            # 5. Reenviar órdenes si corresponde
            if getattr(form_data, "reenviar", False):
                log.info("Acción: Reenviar órdenes.")
                self._page.seleccionar_todas_las_ordenes()
                self._page.reenviar_ordenes()

            # 6. Imprimir órdenes si corresponde y si las dependencias están inyectadas
            if getattr(form_data, "imprimir", False):
                if not (self._file_handler and self._print_service):
                    log.warning("No se inyectaron dependencias de archivo/impresión. Se omite paso de impresión.")
                    return

                log.info("Acción: Imprimir órdenes.")
                self._page.seleccionar_todas_las_ordenes()

                # Obtener PDF y guardarlo
                log.debug(f"Esperando fichero de descarga que contenga: '{filename}'")
                pdf_bytes = self._page.descargar_pdf(filename)
                pdf_path = self._file_handler.save_with_timestamp(pdf_bytes, path, filename)
                log.debug(f"✅ PDF guardado con éxito en: {pdf_path.resolve()}")

                # Enviar a la impresora
                self._print_service.imprimir_fichero(pdf_path)

        except Exception as e:
            log.error(f"Error en ZSIN_ORDENES: {e}", exc_info=True)
            raise
