# pages/mb52_page.py
# Página para la transacción MB52, especializada en la generación de informes de stock

import warnings
from playwright.sync_api import Download, TimeoutError, Error
from core.sap_page_base import SAPPageBase
from core.providers.base_provider import BaseLocatorProvider
from data_models.mb52_models import Mb52FormData
from utils.logger import log

# Componentes
from core.components.sap_form_component import SAPFormComponent
from core.components.sap_form_strategies import SimpleFillStrategy
from core.components.sap_export_dialog import SAPExportDialog

class MB52Page(SAPPageBase):
    def __init__(self, page, locator_provider: BaseLocatorProvider):
        super().__init__(page, locator_provider)

        # --- Locators propios de la página (se quedan) ---
        self.material_input = page.locator(locator_provider.get('form.material'))
        self.centro_input = page.locator(locator_provider.get('form.centro'))
        self.almacen_input = page.locator(locator_provider.get('form.almacen'))
        self.results_table = page.locator(locator_provider.get('results.tabla_resultados'))
        self.confirm = page.locator(locator_provider.get('common.continuar'))
        
        # El botón que abre el diálogo sigue siendo responsabilidad de la página
        self.download_button = page.locator(locator_provider.get('buttons.descargar_hoja'))

        # Componentes:
        self.form = SAPFormComponent(page, locator_provider)
        self.export_dialog = SAPExportDialog(self.page, locator_provider)

        # --- Mapa del Formulario ---
        self.form_map = {
            'material': self.material_input,
            'centro': self.centro_input,
            'almacen': self.almacen_input
        }

    def rellenar_formulario(self, data: Mb52FormData):
        """
        Rellena el formulario (componente formulario) con una estrategia de cumplimentado.
        """
        self.form.fill_form(data, self.form_map, strategy=SimpleFillStrategy())

    def ejecutar_informe(self):
        """
        Ejecuta el informe y espera a que aparezca la tabla de resultados.
        """
        self.execute()

        self.confirm.wait_for()
        self.confirm.click()

        self.results_table.wait_for()

    def is_results_table_visible(self) -> bool:
        """Comprueba si la tabla de resultados del informe está visible."""
        return self.results_table.is_visible()

    def descargar_hoja_calculo(self, fichero_de_salida_nombre: str) -> Download:
        """
        3. El método de descarga ahora es mucho más simple y declarativo.
        Orquesta la descarga abriendo el diálogo y delegando su gestión al componente.
        """
        try:
            with self.page.expect_download() as download_info:
                # La página es responsable de la acción que abre el diálogo
                self.download_button.click()

                # La página delega el manejo del diálogo al componente experto
                self.export_dialog.completar_dialogo(fichero_de_salida_nombre)

            return download_info.value

        except (TimeoutError, Error) as e:
            log.error(f"El proceso de descarga para MB52 ha fallado: {e}")
            raise