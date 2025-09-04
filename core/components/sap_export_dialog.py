# Fichero: core/components/sap_export_dialog.py

from playwright.sync_api import Page
from utils.logger import log
from core.providers.locators.base_locator_provider import BaseLocatorProvider

class SAPExportDialog:
    """
    Gestiona la interacción con el diálogo de SAP que pide un nombre de fichero
    y tiene botones de "Exportar" y "OK".
    """
    def __init__(self, page: Page, locator_provider: BaseLocatorProvider):
        self.page = page
        
        # --- Locators Internos del Componente (los que ya tenías en MB52Page) ---
        self.filename_input = page.locator(locator_provider.get('dialogs.filename_input'))
        self.exportar_a_button = page.locator(locator_provider.get('dialogs.exportar_a'))
        self.ok_button = page.locator(locator_provider.get('common.dialog_ok'))

    def completar_dialogo(self, nombre_fichero: str):
        """
        Completa los pasos del diálogo de exportación.
        La lógica es la misma que tenías en MB52Page.
        """
        log.info(f"Completando diálogo de exportación con el nombre: {nombre_fichero}")
        
        self.filename_input.wait_for()
        self.filename_input.fill(nombre_fichero)
        self.filename_input.press("Enter")

        self.exportar_a_button.wait_for()
        self.exportar_a_button.click()

        self.ok_button.wait_for()
        self.ok_button.click()