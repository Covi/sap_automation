# services/iq09_service.py

import logging
from pathlib import Path
from playwright.sync_api import Error, TimeoutError

from config import Iq09Config
from core.builders.sap_payload_builder import SapPayloadBuilder
from schemas.iq09 import Iq09FormData as FormData
from pages.iq09_page import Iq09Page
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
        """
        try:
            self._transaction_service.run_transaction(self._config.TRANSACTION_CODE)
            self._generar_informe(form_data)
            self.descargar_informe(path, filename)
        except Exception as e:
            log.error(f"Error en {self._config.TRANSACTION_CODE}: {e}", exc_info=True)
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

        # 2. (Opcional) Gestión de Popups 
        # IQ09 a veces tiene popups informativos, no está de más dejarlo.
        # self._page.gestionar_dialogo_emergente("Continuar") 

        # 3. PRIMERO: Buscar error en la barra de estado (ej: "No se seleccionaron objetos")
        # Usamos el método inteligente que ya tienes en SAPPageBase
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
            # Si falla el timeout, volvemos a mirar la barra de estado por si acaso
            # salió un error tarde o un mensaje de tipo 'Info' que impide la carga.
            msg = self._page.get_status_bar_message()
            if msg:
                 raise RuntimeError(f"No se cargó la tabla. Mensaje en status bar: {msg}")
            raise RuntimeError("El informe no se generó: Timeout esperando la tabla de resultados.")

    def descargar_informe(self, fichero_de_salida_path: str, fichero_de_salida_nombre: str):
        # Esta comprobación ahora es redundante pero segura
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