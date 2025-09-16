# services/iq09_service.py

import logging

from config import Iq09Config
from core.builders.sap_payload_builder import SapPayloadBuilder
from schemas.iq09 import Iq09FormData as FormData
from pages.iq09_page import Iq09Page
from playwright.sync_api import Error
from services.transaction_service import TransactionService

log = logging.getLogger(__name__)

class DownloadFailureError(Exception):
    pass

class Iq09Service:
    def __init__(self, transaction_service: TransactionService, iq09_page: Iq09Page):
        self._transaction_service = transaction_service
        self._page = iq09_page
        self._config = Iq09Config
        self.payload = SapPayloadBuilder
        
    def run(self, form_data: FormData, path: str, filename: str):
        """
        Orquesta el flujo completo de la transacción.

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

    def generar_informe(self, form_data: FormData):
        log.debug(f"Iniciando transacción IQ09 con datos: {form_data.model_dump(exclude_none=True)}")
        payload = self.payload.build_payload(form_data)
        self._page.rellenar_formulario(payload)
        self._page.ejecutar()

    def descargar_informe(self, fichero_de_salida_path: str, fichero_de_salida_nombre: str):
        if not self._page.is_results_table_visible():
            raise RuntimeError("No se puede descargar. La tabla de resultados no está visible.")
        log.info(f"Descargando informe en: {fichero_de_salida_path}")

        try:
            download = self._page.descargar_informe()
            download.save_as(fichero_de_salida_path)
            log.info(f"Fichero guardado en: {fichero_de_salida_path}")
        except Error as e:
            log.error(f"Error de Playwright durante la descarga: {e}")
            raise DownloadFailureError("El proceso de descarga ha fallado.") from e