# services/mb52_service.py

# Logging
import logging
log = logging.getLogger(__name__)

from data_models.mb52_models import Mb52FormData
from pages.mb52_page import MB52Page
from playwright.sync_api import Error
from services.transaction_service import TransactionService

class DownloadFailureError(Exception):
    pass

class MB52Service:
    def __init__(self, transaction_service: TransactionService, mb52_page: MB52Page):
        self._transaction_service = transaction_service
        self._mb52_page = mb52_page

    ### CAMBIO: Nuevo método que define el flujo de trabajo de esta transacción ###
    def run(self, form_data: Mb52FormData, path: str, filename: str):
        """
        El "guion" completo para una ejecución de MB52: generar y luego descargar.
        """
        self.generar_informe(form_data)
        self.descargar_informe(path, filename)

    def generar_informe(self, form_data: Mb52FormData):
        self._transaction_service.run_transaction("MB52")
        self._mb52_page.rellenar_formulario(form_data)
        self._mb52_page.ejecutar_informe()

    def descargar_informe(self, fichero_de_salida_path: str, fichero_de_salida_nombre: str):
        # Este método se mantiene sin cambios
        if not self._mb52_page.is_results_table_visible():
            raise RuntimeError("No se puede descargar. La tabla de resultados no está visible.")
        log.info(f"Descargando informe en: {fichero_de_salida_path}")
        try:
            download = self._mb52_page.descargar_hoja_calculo(fichero_de_salida_nombre)
            download.save_as(fichero_de_salida_path)
            log.info(f"Fichero guardado en: {fichero_de_salida_path}")
        except Error as e:
            log.error(f"Error de Playwright durante la descarga: {e}")
            raise DownloadFailureError("El proceso de descarga ha fallado.") from e