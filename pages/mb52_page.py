import logging
from typing import Any, Dict

from playwright.sync_api import Download, TimeoutError, Error

from pages.sap_report_page import SAPReportPage

# Componentes y Estrategias
from core.components.form.sap_form_strategies import SimpleFillStrategy, FormFillingStrategy
from core.components.dialog.sap_export_dialog import SAPExportDialog

log = logging.getLogger(__name__)

class MB52Page(SAPReportPage):
    """
    Page Object Model para la transacción MB52 de SAP.
    Hereda la lógica común de informes de SAPReportPage.
    """
    def __init__(self, page, locator_provider: Any):
        super().__init__(page, locator_provider)

        # --- Definición de componentes y locators específicos de MB52 ---
        self.results_table = self.playwright_page.locator(self._provider.get('results.tabla_resultados'))
        self.confirm_button = self.playwright_page.locator(self._provider.get('common.continuar'))
        self.download_button = self.playwright_page.locator(self._provider.get('buttons.descargar_hoja'))
        self.export_dialog = SAPExportDialog(self)

    # --- Implementación de las propiedades abstractas obligatorias ---

    @property
    def form_locators(self) -> Dict[str, Any]:
        """Provee el mapa de locators del formulario para la clase base."""
        return {
            'material': self.playwright_page.locator(self._provider.get('form.material')),
            'centro': self.playwright_page.locator(self._provider.get('form.centro')),
            'almacen': self.playwright_page.locator(self._provider.get('form.almacen'))
        }

    @property
    def fill_strategy(self) -> FormFillingStrategy:
        """Provee la estrategia de rellenado para la clase base."""
        return SimpleFillStrategy()

    # --- Implementación de los métodos abstractos obligatorios ---

    def _esperar_resultados(self, timeout: int = 30000):
        """Implementa la lógica de espera específica de MB52."""
        self.confirm_button.wait_for(timeout=timeout)
        self.confirm_button.click()
        self.results_table.wait_for(timeout=timeout)

    def is_results_table_visible(self) -> bool:
        """Comprueba si la tabla de resultados del informe está visible."""
        return self.results_table.is_visible()

    def descargar_hoja_calculo(self, fichero_de_salida_nombre: str) -> Download:
        """
        Orquesta la descarga abriendo el diálogo y delegando su gestión al componente.
        """
        try:
            with self.playwright_page.expect_download() as download_info:
                self.download_button.click()
                self.export_dialog.completar_dialogo(fichero_de_salida_nombre)
            return download_info.value
        except (TimeoutError, Error) as e:
            log.error(f"El proceso de descarga para MB52 ha fallado: {e}")
            raise