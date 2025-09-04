# Fichero: core/components/sap_menu_export_dialog.py

from playwright.sync_api import Page, Download
from utils.logger import log
# 1. Se importa el BaseLocatorProvider
from core.providers.locators.base_locator_provider import BaseLocatorProvider

class SAPMenuExportDialog:
    """
    Gestiona la interacción con el diálogo modal de exportación a fichero de SAP.
    """
    # 2. El constructor ahora también recibe el locator_provider
    def __init__(self, page: Page, locator_provider: BaseLocatorProvider):
        self.page = page
        
        # 3. Los locators ahora se leen desde el provider, igual que en las Pages
        #    El prefijo 'menu_export_dialog' se corresponde con la sección en el .toml
        self.radio_texto_con_tabuladores = page.locator(locator_provider.get('menu_export_dialog.radio_texto_con_tabuladores'))
        self.boton_continuar = page.locator(locator_provider.get('menu_export_dialog.boton_continuar'))
        self.formato_dropdown = page.locator(locator_provider.get('menu_export_dialog.formato_dropdown'))
        self.opcion_hoja_calculo = page.locator(locator_provider.get('menu_export_dialog.opcion_hoja_calculo'))
        self.boton_ok = page.locator(locator_provider.get('menu_export_dialog.boton_ok'))

    def exportar_como_spreadsheet(self) -> Download:
        """
        Completa los pasos del diálogo para exportar como hoja de cálculo
        y devuelve el objeto Download resultante. (Este método no cambia)
        """
        log.info("Completando el diálogo de exportación del menú.")
        
        with self.page.expect_download() as download_info:
            self.radio_texto_con_tabuladores.wait_for()
            self.radio_texto_con_tabuladores.check()
            self.boton_continuar.click()

            self.formato_dropdown.wait_for()
            self.formato_dropdown.click()
            self.opcion_hoja_calculo.click()
            
            self.boton_ok.click()
        
        log.info("Descarga iniciada a través del diálogo de exportación.")
        return download_info.value