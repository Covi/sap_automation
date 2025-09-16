import logging
from typing import Any, Dict

from playwright.sync_api import Download, TimeoutError, Error

from .sap_report_page import SAPReportPage

# Componentes y Estrategias
from core.components.form.sap_form_strategies import SimpleFillStrategy, FormFillingStrategy
from core.components.menu.sap_menu_component import SAPMenuComponent
from core.components.dialog.sap_menu_export_dialog import SAPMenuExportDialog
from core.components.table.sap_table_component import SAPTableComponent, GridViewDecorator

log = logging.getLogger(__name__)

class Iq09Page(SAPReportPage):
    """
    Page Object Model para la transacción IQ09 de SAP.
    Hereda la lógica común de informes de SAPReportPage y decora su tabla
    con funcionalidades específicas de GridView.
    """
    def __init__(self, page, locator_provider: Any):
        """
        Inicializa la página, sus componentes y decora la tabla de resultados.
        """
        super().__init__(page, locator_provider)

        # --- Componentes específicos de la página ---
        self.menu = SAPMenuComponent(self)
        self.export_dialog = SAPMenuExportDialog(self)

        # --- Decoración de la tabla de resultados ---
        # 1. Localiza el contenedor principal de la tabla.
        table_locator = self.playwright_page.locator(self._provider.get('results.tabla_resultados'))
        # 2. Crea la instancia base del componente de tabla.
        base_table = SAPTableComponent(self, table_locator)
        # 3. Envuelve la tabla base con el decorador para añadirle las capacidades de GridView.
        #    La clase base (SAPReportPage) usará este componente decorado.
        self.results_table = GridViewDecorator(base_table)

    # --- Implementación de las propiedades abstractas obligatorias ---

    @property
    def form_locators(self) -> Dict[str, Any]:
        """Provee el mapa de locators del formulario para la clase base."""
        return {
            'centro': self.playwright_page.locator(self._provider.get('form.centro')),
            'n_serie': self.playwright_page.locator(self._provider.get('form.n_serie')),
        }

    @property
    def fill_strategy(self) -> FormFillingStrategy:
        """Provee la estrategia de rellenado para la clase base."""
        return SimpleFillStrategy()

    # --- Implementación de los métodos abstractos obligatorios ---

    def _esperar_resultados(self, timeout: int = 30000):
        """
        Implementa la lógica de espera específica de IQ09.
        Usa el método mejorado del componente decorado.
        """
        self.results_table.wait_for_table(timeout=timeout)
        log.debug("Tabla de resultados de IQ09 visible.")

    # --- Métodos específicos de IQ09 que se mantienen ---

    def descargar_informe(self) -> Download:
        """Inicia la descarga a través de la navegación por el menú de SAP."""
        log.info("Iniciando descarga para IQ09 a través del menú SAP...")
        try:
            # Primero nos aseguramos de que hay resultados para descargar
            if not self.hay_resultados():
                raise RuntimeError("No se puede descargar el informe porque no hay resultados en la tabla.")
            
            self.menu.navigate_to("Menú", "Lista", "Grabar", "Fichero...")
            return self.export_dialog.exportar_como_spreadsheet()
        except (TimeoutError, Error) as e:
            log.error(f"El proceso de descarga para IQ09 ha fallado: {e}")
            raise