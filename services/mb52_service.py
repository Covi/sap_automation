# services/mb52_service.py

import logging
from pathlib import Path
from services.transaction_service import TransactionService
from core.builders.sap_payload_builder import SapPayloadBuilder
# FIXME Todo esto debería ser inyectado, no importado directamente
from config import Mb52Config # FIXME Error, debe ser agnóstico a un config en general y no extraer constantes de config
from schemas.mb52 import Mb52FormData
from pages.mb52_page import MB52Page, Error, TimeoutError


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
            self._generar_informe(form_data)
            self._descargar_informe(path, filename)
        except Exception as e:
            log.error(f"Error en {self._config.TRANSACTION_CODE}: {e}", exc_info=True)
            raise

    def _generar_informe(self, form_data: Mb52FormData):
        """
        Rellena el formulario, lo ejecuta y valida el resultado de forma robusta,
        gestionando tanto los casos de éxito como los de error.
        """
        # 1. Rellenar el formulario
        log.info("Rellenando el formulario de MB52...")
        payload = self.payload.build_payload(form_data)
        self._page.rellenar_formulario(payload)

        # 2. Ejecutar la acción principal (ya no espera resultados por sí misma)
        self._page.ejecutar()

        # Si necesitas pulsar "Continuar":
        self._page.gestionar_dialogo_emergente("Continuar")

        # Ahora la lógica es explícita: buscamos un mensaje de tipo "Error".
        error_msg = self._page.check_status_bar_for_message_type("Error")

        if error_msg:
            # Esta sección solo se ejecuta si el mensaje era realmente un error.
            raise ValueError(f"SAP ha devuelto un error fatal: {error_msg}")

        # 5. SEGUNDO: Si no hubo error, ESPERAR y verificar la señal de éxito
        try:
            # Ahora sí, esperamos activamente por la tabla
            self._page.esperar_resultados()
            
            # Como doble confirmación, verificamos que sea visible
            if not self._page.is_results_table_visible():
                raise RuntimeError("La espera ha terminado, pero la tabla de resultados no es visible.")

        except TimeoutError:
            # Si esperar_resultados() falla, lanzamos un error claro
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