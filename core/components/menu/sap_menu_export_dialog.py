# core/components/menu/sap_menu_export_dialog.py

from playwright.sync_api import Download
from utils.logger import log
# Componente base
from .. sap_component import SAPComponent

# Ahora hereda de SAPComponent.
class SAPMenuExportDialog(SAPComponent):
    """
    Gestiona la interacción con el diálogo de exportación del menú de SAP.
    """
    def __init__(self, sap_page):
        # 1. Llama al constructor del padre para inicializar self.playwright_page y self._provider
        super().__init__(sap_page)

        # 2. Añade la inicialización específica de este componente.
        self.dialog_window = self.playwright_page.locator(self._provider.get('common.dialog_export_menu_window'))
        self.guardar_como_textbox = self.playwright_page.locator(self._provider.get('menu_export_dialog.guardar_como_textbox'))
        self.opcion_hoja_calculo = self.playwright_page.locator(self._provider.get('menu_export_dialog.opcion_hoja_calculo'))
        self.boton_ok = self.playwright_page.locator(self._provider.get('menu_export_dialog.boton_ok'))

    def exportar_como_spreadsheet(self) -> Download:
        # El código de este método no necesita cambios, ya que opera
        # con los atributos de la instancia (self.dialog_window, etc.)
        log.info("Completando el diálogo de exportación del menú.")
        self.dialog_window.wait_for()
        with self.playwright_page.expect_download() as download_info:
            self.guardar_como_textbox.click()
            self.opcion_hoja_calculo.click()
            self.boton_ok.click()
        log.info("Descarga iniciada a través del diálogo de exportación.")
        return download_info.value