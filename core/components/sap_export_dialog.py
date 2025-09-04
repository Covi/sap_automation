from utils.logger import log
# Importamos la clase base del componente.
from .sap_component import SAPComponent
from pages.sap_page_base import SAPPageBase


class SAPExportDialog(SAPComponent):
    """
    Gestiona la interacción con el diálogo de SAP que pide un nombre de fichero
    y tiene botones de "Exportar" y "OK".
    """
    def __init__(self, sap_page: SAPPageBase):
        # Llama al constructor del padre para inicializar self.playwright_page y self._provider
        super().__init__(sap_page)

        # --- Locators Internos del Componente (se accede a través de self.playwright_page) ---
        self.filename_input = self.playwright_page.locator(self._provider.get('dialogs.filename_input'))
        self.exportar_a_button = self.playwright_page.locator(self._provider.get('dialogs.exportar_a'))
        self.ok_button = self.playwright_page.locator(self._provider.get('common.dialog_ok'))

    def completar_dialogo(self, nombre_fichero: str):
        """
        Completa los pasos del diálogo de exportación.
        """
        log.info(f"Completando diálogo de exportación con el nombre: {nombre_fichero}")

        self.filename_input.wait_for()
        self.filename_input.fill(nombre_fichero)
        self.filename_input.press("Enter")

        self.exportar_a_button.wait_for()
        self.exportar_a_button.click()

        self.ok_button.wait_for()
        self.ok_button.click()