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

        # FIXME Aquí deberíamos gestionar los posibles errores de validación del formulario
        # El contenedor creo que es msgPanel
        # <div tabindex="0" ti="0" title="No existe ninguna entrada correspondiente a la entrada en el campo Material" class="lsMessageBar lsMessageBar--nowrapping lsMessageBar--width-default lsMessageBar--ruleBottom lsMessageBar--transparent" id="wnd[0]/sbar_msg" ct="MB" lsdata="{&quot;0&quot;:&quot;No existe ninguna entrada correspondiente a la entrada en el campo Material&quot;,&quot;1&quot;:&quot;WARNING&quot;,&quot;5&quot;:&quot;No existe ninguna entrada correspondiente a la entrada en el campo Material&quot;,&quot;6&quot;:true,&quot;7&quot;:&quot;Visualizar detalles&quot;,&quot;11&quot;:{&quot;SID&quot;:&quot;wnd[0]/sbar_msg&quot;,&quot;Type&quot;:&quot;MESSAGEBAR&quot;,&quot;visibility&quot;:0,&quot;messageType&quot;:&quot;Advertencia&quot;,&quot;applicationText&quot;:&quot;No existe ninguna entrada correspondiente a la entrada en el campo Material&quot;},&quot;12&quot;:false,&quot;13&quot;:true}" lsevents="{&quot;ActivateHelp&quot;:[{},{&quot;1&quot;:&quot;action/1/wnd[0]/sbar&quot;,&quot;2&quot;:true}]}" aria-labelledby="wnd[0]/sbar_msg-arialabel" role="note" aria-roledescription="Barra de información" aria-live="assertive" data-toolbaritem-id="wnd[0]/sbar_msg" data-ls-firstitem="true" data-separator-group="0" data-after-priority="0"><span class="lsControl--invisible " id="wnd[0]/sbar_msg-arialabel">Advertencia Barra de mensajes No existe ninguna entrada correspondiente a la entrada en el campo Material</span><span id="wnd[0]/sbar_msg-icon" class="lsMessageBar__icon lsMessageBar__image lsMessageBar__icon--Warning lsMessageBar__image--Warning" role="img" aria-hidden="true"></span><span role="presentation" aria-hidden="true" id="wnd[0]/sbar_msg-txt" class="lsMessageBar__text lsMessageBar__text--overflow" title="No existe ninguna entrada correspondiente a la entrada en el campo Material">No existe ninguna entrada correspondiente a la entrada en el campo Material</span><span class="lsMessageBar__link lsMessageBar__link--noUserSelect" id="wnd[0]/sbar_msg-help" tabindex="0" ti="0" role="link">Visualizar detalles</span></div>


        # 2. Ejecutar la acción principal (ya no espera resultados por sí misma)
        self._page.ejecutar()

        # --- AHORA, EL SERVICIO ORQUESTA LA VALIDACIÓN ---
        
        # 3. Gestionar posibles pop-ups intermedios que bloqueen el flujo
        self._page.gestionar_posible_popup_continuar()

        # 4. PRIMERO: Buscar activamente una señal de error conocida (la barra de estado)
        error_msg = self._page.obtener_error_de_status_bar()
        if error_msg:
            # Si encontramos un error, fallamos inmediatamente con un mensaje claro
            raise ValueError(f"SAP ha devuelto un error de validación: {error_msg}")

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