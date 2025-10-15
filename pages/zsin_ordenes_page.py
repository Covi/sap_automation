# pages/zsin_ordenes_page.py

import logging
from typing import Any, Dict

from .sap_page_base import PlaywrightTimeoutError
from .sap_report_page import SAPReportPage

# Componentes y Estrategias
from core.components.form.sap_form_strategies import RangeFillStrategy, FormFillingStrategy
from core.components.table.sap_table_component import SAPTableComponent
from core.components.decorators.sap_grid_view_decorator import SAPGridViewDecorator

log = logging.getLogger(__name__)

class ZsinOrdenesPage(SAPReportPage):
    """
    Page Object Model para la transacción ZSIN_ORDENES de SAP.
    Hereda la lógica común de informes de SAPReportPage.
    """
    def __init__(self, page: SAPReportPage, locator_provider: Any):
        super().__init__(page, locator_provider)

        # --- Definición de componentes y locators específicos de ZSIN_ORDENES ---
        table_main_locator = self.playwright_page.locator(self._provider.get('results.tabla_cts'))
        base_table = SAPTableComponent(self, table_main_locator)
        self.results_table = SAPGridViewDecorator(base_table)

        self.print_dialog_button = self.playwright_page.locator(self._provider.get('print_dialog.boton_imprimir'))

    # --- Implementación de las propiedades abstractas obligatorias ---

    @property
    def form_locators(self) -> Dict[str, Any]:
        """Provee el mapa de locators del formulario para la clase base."""
        return {
            'status': [self.playwright_page.locator(loc) for loc in self._provider.get('form.status')],
            'mecanico': [self.playwright_page.locator(loc) for loc in self._provider.get('form.mecanico')],
            'clase': [self.playwright_page.locator(loc) for loc in self._provider.get('form.clase')],
            'cliente': [self.playwright_page.locator(loc) for loc in self._provider.get('form.cliente')],
            'fechatope': [self.playwright_page.locator(loc) for loc in self._provider.get('form.fechatope')],
            'fechainicio': [self.playwright_page.locator(loc) for loc in self._provider.get('form.fechainicio')],
            'fechacreacion': [self.playwright_page.locator(loc) for loc in self._provider.get('form.fechaicreacion')]
        }
    
    @property
    def fill_strategy(self) -> FormFillingStrategy:
        """Provee la estrategia de rellenado para la clase base."""
        return RangeFillStrategy()

    # --- Implementación de los métodos abstractos obligatorios ---

    def esperar_resultados(self, timeout: int = 30000) -> None:
        """
        ⚠️ CAMBIO: Antes era _esperar_resultados privado. Ahora es público.
        Implementa la lógica de espera específica de ZSIN_ORDENES.
        Debe ser llamado explícitamente desde el flujo que lo necesite.
        """
        log.debug(f"Esperando hasta {timeout / 1000} segundos a que aparezca la tabla de resultados...")
        self.wait_for_page_to_be_ready(timeout=timeout)
        self.results_table.is_visible(timeout=timeout)


    # --- Métodos específicos de ZSIN_ORDENES que se mantienen ---
    def obtener_resultados(self) -> int:
        """Retorna la cantidad de resultados."""
        return self.results_table.get_total_row_count()

    def hay_resultados(self) -> bool:
        """Indica si la tabla tiene resultados reales."""
        return self.obtener_resultados() > 0

    def seleccionar_todas_las_ordenes(self):
        self.results_table.select_all()

    def reenviar_ordenes(self):
        self.results_table.click_toolbar_button("Reenviar")
        self.playwright_page.wait_for_timeout(5000)

    def imprimir_ordenes(self):
        self.results_table.click_toolbar_button("IMPRESIÓN")
        self.playwright_page.wait_for_timeout(5000)

    def descargar_pdf(self, nombre_fichero_esperado: str) -> bytes:
        """Captura la respuesta de red que contiene el PDF de impresión."""
        log.debug("Iniciando proceso de impresión y captura de PDF...")
        try:
            with self.playwright_page.expect_response(
                lambda response: nombre_fichero_esperado in response.url and "application/pdf" in response.headers.get("content-type", ""),
                timeout=90000
            ) as response_info:
                self.imprimir_ordenes()
                self.print_dialog_button.click()

            response = response_info.value
            if response.status != 200:
                raise ConnectionError(f"La descarga del PDF falló con status {response.status}")
            
            log.debug("Respuesta de PDF capturada con éxito.")
            return response.body()
        except PlaywrightTimeoutError:
            log.debug("Timeout esperando la respuesta del PDF. El proceso de impresión falló.")
            raise