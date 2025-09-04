from playwright.sync_api import Download, Locator
from utils.logger import log
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
            self.opcion_guardar_hoja_calculo.click()
            self.boton_ok.click()

        log.info("Descarga iniciada a través del diálogo de exportación.")
        return download_info.value