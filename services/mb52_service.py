# services/mb52_service.py

import logging
from pathlib import Path

# Typing imports: Usamos el type hint específico
from config.settings import Mb52Config
from services.transaction_service import TransactionService
from core.builders.sap_payload_builder import SapPayloadBuilder
from schemas.mb52 import Mb52FormData
from pages.mb52_page import MB52Page, Error, TimeoutError

log = logging.getLogger(__name__)

class DownloadFailureError(Exception):
    pass

class MB52Service:
    def __init__(
        self, 
        transaction_service: TransactionService, 
        page: MB52Page, 
        config: Mb52Config # <--- INYECCIÓN DE DEPENDENCIA
    ):
        self._transaction_service = transaction_service
        self._page = page
        self._config = config # Almacenamos la instancia de configuración
        self.payload = SapPayloadBuilder

    def run(self, form_data: Mb52FormData, path: Path, filename: str):
        """
        Orquesta el flujo completo de la transacción MB52.
        """
        try:
            # Accedemos a los atributos en minúscula (Pydantic model)
            self._transaction_service.run_transaction(self._config.transaction_code)
            self._generar_informe(form_data)
            self._descargar_informe(path, filename)
        except Exception as e:
            log.error(f"Error en {self._config.transaction_code}: {e}", exc_info=True)
            raise

    def _generar_informe(self, form_data: Mb52FormData):
        log.info("Rellenando el formulario de MB52...")
        payload = self.payload.build_payload(form_data)
        self._page.rellenar_formulario(payload)

        self._page.ejecutar()
        self._page.gestionar_dialogo_emergente("Continuar")

        error_msg = self._page.check_status_bar_for_message_type("Error")
        if error_msg:
            raise ValueError(f"SAP ha devuelto un error fatal: {error_msg}")

        try:
            self._page.esperar_resultados()
            if not self._page.is_results_table_visible():
                raise RuntimeError("La espera ha terminado, pero la tabla de resultados no es visible.")
        except TimeoutError:
            raise RuntimeError("El informe no se generó: No se encontró ni un mensaje de error ni la tabla de resultados tras 30s.")
        
        log.info("Informe generado con éxito.")

    def _descargar_informe(self, fichero_de_salida_path: Path, fichero_de_salida_nombre: str):
        log.info(f"Descargando informe en: {fichero_de_salida_path}")
        try:
            download = self._page.descargar_hoja_calculo(fichero_de_salida_nombre)
            download.save_as(fichero_de_salida_path)
            log.info(f"Fichero guardado en: {fichero_de_salida_path}")
        except Error as e:
            log.error(f"Error de Playwright durante la descarga: {e}")
            raise DownloadFailureError("El proceso de descarga ha fallado.") from e