# services/iq09_service.py

import logging
from pathlib import Path
from playwright.sync_api import Error, TimeoutError

# CAMBIO: Importamos desde settings para Type Hinting
from config.settings import Iq09Config
from core.builders.sap_payload_builder import SapPayloadBuilder
from schemas.iq09 import Iq09FormData as FormData
from pages.iq09_page import Iq09Page
from services.transaction_service import TransactionService

log = logging.getLogger(__name__)

class DownloadFailureError(Exception):
    pass

class Iq09Service:
    def __init__(
        self, 
        transaction_service: TransactionService, 
        iq09_page: Iq09Page,
        config: Iq09Config  # <--- INYECCIÓN DE DEPENDENCIA
    ):
        self._transaction_service = transaction_service
        self._page = iq09_page
        self._config = config # Guardamos la instancia inyectada
        self.payload = SapPayloadBuilder
        
    def run(self, form_data: FormData, path: Path, filename: str):
        """
        Orquesta el flujo completo de la transacción.
        """
        try:
            # CAMBIO: Acceso a atributo en minúscula (Pydantic)
            self._transaction_service.run_transaction(self._config.transaction_code)
            self._generar_informe(form_data)
            self.descargar_informe(path, filename)
        except Exception as e:
            # CAMBIO: Acceso a atributo en minúscula
            log.error(f"Error en {self._config.transaction_code}: {e}", exc_info=True)
            raise

    def _generar_informe(self, form_data: FormData):
        """
        Rellena, ejecuta y VALIDA el resultado.
        """
        log.debug(f"Iniciando transacción IQ09 con datos: {form_data.model_dump(exclude_none=True)}")
        
        # 1. Rellenar y Ejecutar
        payload = self.payload.build_payload(form_data)
        self._page.rellenar_formulario(payload)
        self._page.ejecutar()

        # 2. (Opcional) Gestión de Popups FIXME Esto tiene un nombre muy raro, no mola
        # self._page.gestionar_dialogo_emergente("Continuar") 

        # 3. PRIMERO: Buscar error en la barra de estado
        error_msg = self._page.check_status_bar_for_message_type("Error")
        if error_msg:
            raise ValueError(f"SAP ha devuelto un error de validación: {error_msg}")

        # 4. SEGUNDO: Esperar a la tabla de resultados
        try:
            log.debug("Esperando resultados...")
            self._page.esperar_resultados()

            # Doble verificación
            if not self._page.is_results_table_visible():
                 raise RuntimeError("La espera terminó pero la tabla no es visible.")
                 
        except TimeoutError:
            # Si falla el timeout, volvemos a mirar la barra de estado
            msg = self._page.get_status_bar_message()
            if msg:
                 raise RuntimeError(f"No se cargó la tabla. Mensaje en status bar: {msg}")
            raise RuntimeError("El informe no se generó: Timeout esperando la tabla de resultados.")

    def descargar_informe(self, fichero_de_salida_path: Path, fichero_de_salida_nombre: str):
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