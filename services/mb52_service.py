# services/mb52_service.py

import logging
from pathlib import Path

from config import Mb52Config
from pages.mb52_page import MB52Page, Error
from services.transaction_service import TransactionService
from schemas.mb52 import Mb52FormData

from core.builders.sap_payload_builder import SapPayloadBuilder

log = logging.getLogger(__name__)

class DownloadFailureError(Exception):
    pass

class MB52Service:
    def __init__(self, transaction_service: TransactionService, page: MB52Page):
        self._transaction_service = transaction_service
        self._page = page
        self._config = Mb52Config
        self.payload = SapPayloadBuilder

    def run(self, form_data: Mb52FormData, path: Path, filename: str):
        """
        Orquesta el flujo completo de la transacción ZSIN_ORDENES.

        :param form_data: Datos del formulario a enviar.
        :param path: Directorio donde guardar ficheros descargados.
        :param filename: Nombre del fichero a generar.
        """
        try:
            # 1. Entrar en la transacción
            self._transaction_service.run_transaction(self._config.TRANSACTION_CODE)
            self.generar_informe(form_data)
            self.descargar_informe(path, filename)
        except Exception as e:
            log.error(f"Error en {self._config.TRANSACTION_CODE}: {e}", exc_info=True)
            raise

    def generar_informe(self, form_data: Mb52FormData):
        payload = self.payload.build_payload(form_data)
        self._page.rellenar_formulario(payload)
        self._page.ejecutar_informe()

    def descargar_informe(self, fichero_de_salida_path: Path, fichero_de_salida_nombre: str):
        if not self._page.is_results_table_visible():
            raise RuntimeError("No se puede descargar. La tabla de resultados no está visible.")
        log.info(f"Descargando informe en: {fichero_de_salida_path}")

        try:
            download = self._page.descargar_hoja_calculo(fichero_de_salida_nombre)
            download.save_as(fichero_de_salida_path)
            log.info(f"Fichero guardado en: {fichero_de_salida_path}")
        except Error as e:
            log.error(f"Error de Playwright durante la descarga: {e}")
            raise DownloadFailureError("El proceso de descarga ha fallado.") from e