# sap_ui/sap_export_dialog.py

from playwright.sync_api import Locator

class SAPExportDialog:
    def __init__(self, filename_input: Locator, export_button: Locator, ok_button: Locator):
        self.filename_input = filename_input
        self.export_button = export_button
        self.ok_button = ok_button

    def completar_dialogo(self, nombre_fichero: str):
        self.filename_input.wait_for()
        self.filename_input.fill(nombre_fichero)
        self.filename_input.press("Enter")

        self.export_button.wait_for()
        self.export_button.click()

        self.ok_button.wait_for()
        self.ok_button.click()
