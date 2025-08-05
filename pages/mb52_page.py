# pages/mb52_page.py
# Página para la transacción MB52, especializada en la generación de informes de stock

from playwright.sync_api import Download, TimeoutError, Error
from core.sap_page_base import SAPPageBase
from core.providers.base_provider import BaseLocatorProvider
from data_models.mb52_models import Mb52FormData

class MB52Page(SAPPageBase):
    def __init__(self, page, locator_provider: BaseLocatorProvider):
        super().__init__(page, locator_provider)

        # --- Locator provider
        self.locator_provider = locator_provider

        # --- Locators específicos (incluyendo los de descarga) ---
        self.material_input = page.locator(locator_provider.get('form.material'))
        self.centro_input = page.locator(locator_provider.get('form.centro'))
        self.almacen_input = page.locator(locator_provider.get('form.almacen'))
        self.results_table = page.locator(locator_provider.get('results.tabla_resultados'))

        self.confirm = page.locator(locator_provider.get('common.continuar'))
        self.ok_button = page.locator(locator_provider.get('common.dialog_ok'))

        # Descarga
        self.download_button = page.locator(locator_provider.get('buttons.descargar_hoja'))
        self.filename_dialog_input = page.locator(locator_provider.get('dialogs.filename_input'))
        self.exportar_a_button = page.locator(locator_provider.get('dialogs.exportar_a'))

        # --- Mapa del Formulario ---
        self.form_map = {
            'material': self.material_input,
            'centro': self.centro_input,
            'almacen': self.almacen_input
        }

    def rellenar_formulario(self, data: Mb52FormData):
        """
        Rellena el formulario de MB52 llamando al método genérico del padre.
        """
        self._fill_form(self.form_map, data)

    def ejecutar_informe(self):
        """
        Ejecuta el informe y espera a que aparezca la tabla de resultados.
        """
        self.execute() # Método heredado, pulsa botón de ejecutar ([id='M0:50::btn[8]'])

        # Espera a que el botón de continuar esté visible y lo hace clic
        self.confirm.wait_for()
        self.confirm.click()

        # Espera a que la tabla de resultados esté visible
        self.results_table.wait_for()

    def is_results_table_visible(self) -> bool:
        """Comprueba si la tabla de resultados del informe está visible."""
        return self.results_table.is_visible()

    def descargar_hoja_calculo(self, fichero_de_salida_nombre: str) -> Download:
        """
        Orquesta la interacción UI para iniciar la descarga y devuelve el objeto Download.
        """
        try:
            with self.page.expect_download() as download_info:
                self.download_button.wait_for()
                self.download_button.click()

                self.filename_dialog_input.wait_for()
                self.filename_dialog_input.fill(fichero_de_salida_nombre)
                self.filename_dialog_input.press("Enter")

                self.exportar_a_button.wait_for()
                self.exportar_a_button.click()

                self.ok_button.wait_for()
                self.ok_button.click()

            download = download_info.value
            return download

        except (TimeoutError, Error):
            raise