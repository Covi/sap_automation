# pages/mb52_page.py
# Página para la transacción MB52, especializada en la generación de informes de stock

from typing import Any
from playwright.sync_api import Download, TimeoutError, Error
from .sap_page_base import SAPPageBase
from data_models.mb52_models import Mb52FormData
from utils.logger import log

# Componentes
from core.components.sap_form_component import SAPFormComponent
from core.components.sap_form_strategies import SimpleFillStrategy
from core.components.sap_export_dialog import SAPExportDialog

class MB52Page(SAPPageBase):
    # CAMBIO: El constructor se simplifica y no necesita el tipo explícito del provider.
    def __init__(self, page, locator_provider: Any):
        # La llamada a super() se encarga de todo lo relacionado con el provider.
        super().__init__(page, locator_provider)

        # --- Locators propios de la página (usando self._provider heredado) ---
        self.material_input = page.locator(self._provider.get('form.material'))
        self.centro_input = page.locator(self._provider.get('form.centro'))
        self.almacen_input = page.locator(self._provider.get('form.almacen'))
        self.results_table = page.locator(self._provider.get('results.tabla_resultados'))
        self.confirm = page.locator(self._provider.get('common.continuar'))
        self.download_button = page.locator(self._provider.get('buttons.descargar_hoja'))

        # --- Componentes ---
        # La instanciación de componentes sigue igual, pero ahora pasamos el provider heredado.
        self.form = SAPFormComponent(page, self._provider)
        self.export_dialog = SAPExportDialog(self.page, self._provider)

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
        self.execute() # Usa el método execute() heredado de SAPPageBase

        self.confirm.wait_for()
        self.confirm.click()

        self.results_table.wait_for()

    def is_results_table_visible(self) -> bool:
        """Comprueba si la tabla de resultados del informe está visible."""
        return self.results_table.is_visible()

    def descargar_hoja_calculo(self, fichero_de_salida_nombre: str) -> Download:
        """
        Orquesta la descarga abriendo el diálogo y delegando su gestión al componente.
        """
        try:
            with self.page.expect_download() as download_info:
                self.download_button.click()
                self.export_dialog.completar_dialogo(fichero_de_salida_nombre)
            return download_info.value
        except (TimeoutError, Error) as e:
            log.error(f"El proceso de descarga para MB52 ha fallado: {e}")
            raise