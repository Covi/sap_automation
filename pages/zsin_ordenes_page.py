import logging
from typing import Any, Dict

from .sap_report_page import SAPReportPage
from .sap_page_base import PlaywrightTimeoutError

# Componentes y Estrategias
from core.components.form.sap_form_strategies import RangeFillStrategy, FormFillingStrategy
from core.components.table.sap_table_component import SAPTableComponent, GridViewDecorator

log = logging.getLogger(__name__)

class ZsinOrdenesPage(SAPReportPage):
    """
    Page Object Model para la transacción ZSIN_ORDENES de SAP.
    Hereda la lógica común de informes de SAPReportPage.
    """
    def __init__(self, page: SAPReportPage, locator_provider: Any):
        super().__init__(page, locator_provider)

        # --- Componentes ---
        table_main_locator = self.playwright_page.locator(self._provider.get('results.tabla'))
        # Se aplica el patrón Decorator
        base_table = SAPTableComponent(self, table_main_locator)
        self.results_table = GridViewDecorator(base_table)

        # --- Locators de la página ---
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

    # --- Implementación del método abstracto obligatorio ---

    def _esperar_resultados(self, timeout: int = 30000) -> None:
        """Implementa la lógica de espera específica de ZSIN_ORDENES."""
        log.debug(f"Esperando hasta {timeout / 1000} segundos a que aparezca la tabla de resultados...")
        # FIXME: Esto no funca
        self._loading_disappear(timeout=timeout)
        self.results_table.wait_for_table(timeout=timeout)

    # --- Métodos que se eliminan por estar en la clase base ---
    # rellenar_formulario()
    # ejecutar_busqueda() (ahora se usa el método 'ejecutar()' heredado)
    # hay_resultados() (ahora se usa el método heredado)

    # --- Métodos que se mantienen porque son parte de la API que usa el Servicio ---
    
    def obtener_resultados(self) -> int:
        """Retorna la cantidad de resultados."""
        return self.results_table.get_total_row_count()

    # --- Métodos específicos de ZSIN_ORDENES que se mantienen ---

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
            # Ahora usa el método 'hay_resultados' heredado de la clase base
            if not self.hay_resultados():
                 raise RuntimeError("No se puede descargar el PDF porque no hay resultados en la tabla.")

            with self.playwright_page.expect_response(
                lambda response: nombre_fichero_esperado in response.url and "application/pdf" in response.headers.get("content-type", ""),
                timeout=90000
            ) as response_info:
                self.imprimir_ordenes()
                self.print_dialog_button.wait_for()
                self.print_dialog_button.click()

            response = response_info.value
            if response.status != 200:
                raise ConnectionError(f"La descarga del PDF falló con status {response.status}")
            
            log.debug("Respuesta de PDF capturada con éxito.")
            return response.body()
        except PlaywrightTimeoutError:
            log.debug("Timeout esperando la respuesta del PDF. El proceso de impresión falló.")
            raise