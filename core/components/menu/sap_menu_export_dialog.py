# core/components/menu/sap_menu_export_dialog.py

from playwright.sync_api import Download
from utils.logger import log
# Componente base
from .. sap_component import SAPComponent

class SAPMenuExportDialog(SAPComponent):
    """
    Gestiona la interacción con el diálogo de exportación del menú de SAP.
    """
    def __init__(self, sap_page):
        # Llama al constructor del padre para inicializar self.playwright_page y self._provider
        super().__init__(sap_page)
        page = self.playwright_page
        locator_provider = self._provider

        # Los locators ahora se leen desde el provider, igual que en las Pages
        #    El prefijo 'menu_export_dialog' se corresponde con la sección en el .toml
        self.radio_texto_con_tabuladores = page.locator(locator_provider.get('menu_export_dialog.radio_texto_con_tabuladores'))
        self.boton_continuar = page.locator(locator_provider.get('menu_export_dialog.boton_continuar'))
        self.guardar_como_textbox = page.locator(locator_provider.get('menu_export_dialog.guardar_como_textbox'))
        self.opcion_hoja_calculo = page.locator(locator_provider.get('menu_export_dialog.opcion_hoja_calculo'))
        self.boton_ok = page.locator(locator_provider.get('menu_export_dialog.boton_ok'))

    def exportar_como_spreadsheet(self) -> Download:
        """
        Completa los pasos del diálogo para exportar como hoja de cálculo
        y devuelve el objeto Download resultante. (Este método no cambia)
        """
        log.info("Completando el diálogo de exportación del menú.")

        with self.playwright_page.expect_download() as download_info:
            self.radio_texto_con_tabuladores.check()
            self.boton_continuar.click()
            self.guardar_como_textbox.click()
            self.opcion_hoja_calculo.click()
            self.boton_ok.click()
        
        log.info("Descarga iniciada a través del diálogo de exportación.")
        return download_info.value
