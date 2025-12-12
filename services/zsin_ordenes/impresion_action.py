# services/zsin_ordenes/impresion_action.py
import logging
from pathlib import Path

# Importamos los protocolos desde su nueva ubicación
from core.protocols import FileHandlerProtocol, PrintServiceProtocol
from pages.zsin_ordenes_page import ZsinOrdenesPage

class ImpresionOrdenesService:
    def __init__(
        self, 
        page: ZsinOrdenesPage, 
        file_handler: FileHandlerProtocol, 
        print_service: PrintServiceProtocol, 
        logger: logging.Logger
    ):
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