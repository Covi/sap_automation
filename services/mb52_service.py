# services/mb52_service.py

from data_models.mb52_models import Mb52FormData
from pages.mb52_page import MB52Page
from playwright.sync_api import Error
from services.transaction_service import TransactionService
from utils.logger import log

class DownloadFailureError(Exception):
    pass

class MB52Service:
    def __init__(self, transaction_service: TransactionService, mb52_page: MB52Page):
        self._transaction_service = transaction_service
        self._mb52_page = mb52_page

    def generar_informe(self, form_data: Mb52FormData):
        # form_data ya está validado por Pydantic v2 al crear la instancia
        self._transaction_service.run_transaction("MB52")
        self._mb52_page.rellenar_formulario(form_data)
        self._mb52_page.ejecutar_informe()

    def descargar_informe(self, fichero_de_salida_path: str, fichero_de_salida_nombre: str):
        if not self._mb52_page.is_results_table_visible():
            raise RuntimeError("No se puede descargar. La tabla de resultados no está visible.")

        log.info(f"Descargando informe en: {fichero_de_salida_path}")

        try:
            download = self._mb52_page.descargar_hoja_calculo(fichero_de_salida_nombre)
            download.save_as(fichero_de_salida_path)
            log.info(f"Fichero guardado en: {fichero_de_salida_path}")
        except Error as e:
            log.error(f"Error de Playwright durante la descarga: {e}")
            raise DownloadFailureError("El proceso de descarga ha fallado. Revisa los logs para más detalles.") from e
