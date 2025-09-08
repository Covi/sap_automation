# services/iq09_service.py

# Logging
import logging
log = logging.getLogger(__name__)

from data_models.iq09_models import Iq09FormData
from pages.iq09_page import Iq09Page
from playwright.sync_api import Error
from services.transaction_service import TransactionService

class DownloadFailureError(Exception):
    pass

class Iq09Service:
    def __init__(self, transaction_service: TransactionService, iq09_page: Iq09Page):
        self._transaction_service = transaction_service
        self._iq09_page = iq09_page
        
    ### CAMBIO: Nuevo método que define el flujo de trabajo de esta transacción ###
    def run(self, form_data: Iq09FormData, path: str, filename: str):
        """
        El "guion" completo para una ejecución de IQ09.
        Si no necesitara descargar, se quitaría la segunda línea.
        """
        self.generar_informe(form_data)
        self.descargar_informe(path, filename)

    def generar_informe(self, form_data: Iq09FormData):
        log.info(f"Iniciando transacción IQ09 con datos: {form_data.model_dump(exclude_none=True)}")
        self._transaction_service.run_transaction("IQ09")
        self._iq09_page.rellenar_formulario(form_data)
        self._iq09_page.ejecutar_informe()

    def descargar_informe(self, fichero_de_salida_path: str, fichero_de_salida_nombre: str):
        log.info(f"Descargando informe de IQ09 en: {fichero_de_salida_path}")
        try:
            # Ahora esta llamada funcionará, porque la página devolverá un objeto Download válido
            download = self._iq09_page.descargar_informe()
            download.save_as(fichero_de_salida_path)
            log.info(f"Fichero de IQ09 guardado en: {fichero_de_salida_path}")
        except Error as e:
            log.error(f"Error de Playwright durante la descarga de IQ09: {e}")
            raise DownloadFailureError("El proceso de descarga de IQ09 ha fallado.") from e