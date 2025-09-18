# core/components/dialog/sap_export_dialog.py

# Logging
import logging
log = logging.getLogger(__name__)

from .base_dialog import BaseDialog
from playwright.sync_api import Locator

class SAPExportDialog(BaseDialog):
    """
    Gestiona la interacción con el diálogo de SAP que pide un nombre de fichero
    y tiene botones de "Exportar" y "OK".
    """
    LOCATOR_SECTION = "export_dialog" # Usamos un nombre de sección semántico y agnóstico
    _specific_locators = [
        "filename_input",
        "exportar_a_button",
    ]

    # Declaramos los atributos para Pylance
    filename_input: Locator
    exportar_a_button: Locator

    def __init__(self, sap_page):
        # El BaseDialog se encarga de inicializar los locators
        super().__init__(sap_page)

    def completar_dialogo(self, nombre_fichero: str):
        """
        Completa los pasos del diálogo de exportación.
        """
        log.info(f"Completando diálogo de exportación con el nombre: {nombre_fichero}")

        self.filename_input.wait_for()
        self.filename_input.fill(nombre_fichero)
        self.filename_input.press("Enter")

        self.exportar_a_button.click()

        self.boton_ok.click()