# Fichero: core/components/sap_export_dialog.py

from playwright.sync_api import Page
from utils.logger import log

class SAPExportDialog:
    """
    Gestiona la interacción con el diálogo de SAP que pide un nombre de fichero
    y tiene botones de "Exportar" y "OK".
    
    NOTA: Este es el componente para el flujo original (tipo MB52).
    """
    def __init__(self, page: Page):
        """
        El constructor ahora recibe 'page' y define sus propios locators internamente.
        """
        self.page = page
        
        # FIXME: Rellenar con los locators correctos para este diálogo específico.
        # Estos son los localizadores que antes se pasaban desde fuera.
        self.filename_input = page.locator('...') 
        self.export_button = page.locator('...')
        self.ok_button = page.locator('...')

    def completar_dialogo(self, nombre_fichero: str):
        """
        Este método se mantiene EXACTAMENTE IGUAL que en tu versión original.
        Su lógica y propósito no han cambiado.
        """
        log.info(f"Completando diálogo de exportación con el nombre: {nombre_fichero}")
        self.filename_input.wait_for()
        self.filename_input.fill(nombre_fichero)
        self.filename_input.press("Enter")

        self.export_button.wait_for()
        self.export_button.click()

        self.ok_button.wait_for()
        self.ok_button.click()