# core/components/dialog/sap_menu_export_dialog.py

# Logging
import logging
log = logging.getLogger(__name__)

from playwright.sync_api import Download, Locator, TimeoutError as PlaywrightTimeoutError
from core.components.dialog.base_dialog import BaseDialog

class SAPMenuExportDialog(BaseDialog):
    """
    Gestiona la interacción con el diálogo de exportación del menú de SAP.
    """
    LOCATOR_SECTION = "menu_export_dialog"
    _specific_locators = [
        "titulo",
        "opcion_exportar_csv",
        "nombre_archivo",
        "opcion_guardar_hoja_calculo"
    ]

    # Declaración de atributos para que Pylance los reconozca
    titulo: Locator
    opcion_exportar_csv: Locator
    nombre_archivo: Locator
    opcion_guardar_hoja_calculo: Locator

    def exportar_como_spreadsheet(self) -> Download:
        log.info("Completando el diálogo de exportación del menú.")
        self.titulo.wait_for(state="visible")
        log.debug("Diálogo de exportación visible.")

        with self.playwright_page.expect_download() as download_info:
            self.opcion_exportar_csv.check()
            self.boton_continuar.click()
            self.nombre_archivo.click()
            try:
                # Espera implícita de Playwright para visibilidad.
                # Intenta el clic normal.
                self.opcion_guardar_hoja_calculo.click(timeout=3000)
            except PlaywrightTimeoutError:
                log.error("El clic normal falló. Intentando con fuerza.")
                # Si el clic normal falla, lo intentamos forzado.
                self.opcion_guardar_hoja_calculo.click(force=True)

            self.boton_ok.click()

        log.info("Descarga iniciada a través del diálogo de exportación.")
        return download_info.value