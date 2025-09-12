# pages/zsin_ordenes_page.py

import logging
from typing import Any

# POM
from .sap_page_base import SAPPageBase, PlaywrightTimeoutError
from core.components.form.sap_form_component import SAPFormComponent
from core.components.form.sap_form_strategies import RangeFillStrategy
from core.components.table.sap_table_component import SAPTableComponent

log = logging.getLogger(__name__)

class ZsinOrdenesPage(SAPPageBase):
    def __init__(self, page: SAPPageBase, locator_provider: Any):
        super().__init__(page, locator_provider)

        # --- Componentes ---
        self.form = SAPFormComponent(self)
        table_main_locator = self.playwright_page.locator(self._provider.get('results.tabla'))
        self.results_table = SAPTableComponent(self, table_main_locator)

        # --- Locators de la página ---
        self.form_locators = {
            'status': [self.playwright_page.locator(loc) for loc in self._provider.get('form.status')],
            'mecanico': [self.playwright_page.locator(loc) for loc in self._provider.get('form.mecanico')],
            'clase': [self.playwright_page.locator(loc) for loc in self._provider.get('form.clase')],
            'cliente': [self.playwright_page.locator(loc) for loc in self._provider.get('form.cliente')],
            'fechatope': [self.playwright_page.locator(loc) for loc in self._provider.get('form.fechatope')],
            'fechainicio': [self.playwright_page.locator(loc) for loc in self._provider.get('form.fechainicio')],
            'fechacreacion': [self.playwright_page.locator(loc) for loc in self._provider.get('form.fechaicreacion')]
        }

        self.print_dialog_button = self.playwright_page.locator(self._provider.get('print_dialog.boton_imprimir'))

    def _esperar_resultados_old(self, timeout: int = 10) -> None:
        log.debug(f"Esperando hasta {timeout} segundos a que aparezca la tabla de resultados...")
        self.results_table.table_locator.wait_for(
            state="visible", 
            timeout=timeout * 1000  # pasar de segundos a ms
        )

    def _esperar_resultados(self, timeout: int = 10) -> None:
        log.debug(f"Esperando hasta {timeout} segundos a que aparezca la tabla de resultados...")

        # Primero esperamos a que desaparezca el indicador de carga de SAP
        # FIXME Esto no funca
        self._loading_disappear(timeout=timeout * 1000)
        # Luego esperamos a que la tabla sea visible
        self.results_table.is_visible(timeout=timeout * 1000)

    def rellenar_formulario(self, payload: dict):
        """
        Rellena el formulario a partir de un payload (dict) pre-formateado.
        """
        strategy = RangeFillStrategy()
        self.form.fill_form(payload, self.form_locators, strategy)

    def ejecutar_busqueda(self):
        """Hace clic en el botón de búsqueda, sin esperar resultados."""
        log.debug("Ejecutando búsqueda en ZSIN_ORDENES...")
        self.execute()
        self._esperar_resultados(timeout=30)

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
        log.debug("Iniciando proceso de impresión y captura de PDF...")
        try:
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