# pages/zsin_ordenes_page.py

import logging
from typing import Any, Dict, List
from .sap_report_page import SAPReportPage
from core.components.table.sap_table_component import SAPTableComponent
from core.components.decorators.sap_grid_view_decorator import SAPGridViewDecorator

log = logging.getLogger(__name__)

class ZsinOrdenesPage(SAPReportPage):
    """
    Page Object Model para la transacción ZSIN_ORDENES de SAP.
    """
    def __init__(self, page: SAPReportPage, locator_provider: Any):
        super().__init__(page, locator_provider)


        # Locators:
        # Tabla de resultados
        table_main_locator = self.playwright_page.locator(self._provider.get('results.tabla_cts'))
        base_table = SAPTableComponent(self, table_main_locator)
        self.results_table = SAPGridViewDecorator(base_table)

        #self.print_dialog_button = self.playwright_page.locator(self._provider.get('print_dialog.boton_imprimir'))
        self.print_dialog_button = self.playwright_page.get_by_role('button', name='Visualización de impresión')

    @property
    def form_locators(self) -> Dict[str, Any]:
        return {
            'status': [self.playwright_page.locator(loc) for loc in self._provider.get('form.status')],
            'mecanico': [self.playwright_page.locator(loc) for loc in self._provider.get('form.mecanico')],
            'clase': [self.playwright_page.locator(loc) for loc in self._provider.get('form.clase')],
            'cliente': [self.playwright_page.locator(loc) for loc in self._provider.get('form.cliente')],
            'fechatope': [self.playwright_page.locator(loc) for loc in self._provider.get('form.fechatope')],
            'fechainicio': [self.playwright_page.locator(loc) for loc in self._provider.get('form.fechainicio')],
            'fechacreacion': [self.playwright_page.locator(loc) for loc in self._provider.get('form.fechaicreacion')]
        }

    def esperar_resultados(self, timeout: int = 30000) -> None:
        log.debug(f"Esperando hasta {timeout/1000} segundos a que aparezca la tabla de resultados...")
        self.wait_for_page_to_be_ready(timeout=timeout)
        self.results_table.is_visible(timeout=timeout)

    # --- Métodos específicos ---
    def obtener_resultados(self) -> int:
        return self.results_table.get_total_row_count()

    def hay_resultados(self) -> bool:
        return self.obtener_resultados() > 0

    def extraer_resultados_estructurados(self) -> List[Dict[str, str]]:
        """
        Combina la metadata de columnas con los datos de las filas para generar
        una lista de diccionarios {ID_COLUMNA: VALOR}.
        """
        # 1. Obtenemos nombres de columnas (Metadata)
        headers = self.results_table.get_column_names()
        
        # 2. Obtenemos datos crudos (DOM)
        raw_rows = self.results_table.get_all_rows_data()
        
        structured_data = []
        
        if not headers:
            log.warning("No se obtuvieron cabeceras. Se devolverán datos sin claves.")
            # Fallback simple si falla la metadata
            return [{"data": str(row)} for row in raw_rows]

        # 3. Mapeo (Zip)
        for row in raw_rows:
            # zip corta en la longitud más corta, evitando errores de índice
            row_dict = dict(zip(headers, row))
            structured_data.append(row_dict)
            
        log.info(f"Datos estructurados extraídos: {len(structured_data)} registros.")
        return structured_data

    def seleccionar_todas_las_ordenes(self):
        self.results_table.select_all()

    # Post Resultados

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
                lambda response: nombre_fichero_esperado in response.url 
                                 and "application/pdf" in response.headers.get("content-type", ""),
                timeout=90000
            ) as response_info:
                self.imprimir_ordenes()
                self.print_dialog_button.click()
            response = response_info.value
            if response.status != 200:
                raise ConnectionError(f"Descarga de PDF fallida con status {response.status}")
            return response.body()
        except Exception:
            log.debug("Timeout o error capturando PDF.")
            raise
