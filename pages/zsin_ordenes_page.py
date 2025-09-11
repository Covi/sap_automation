# pages/zsin_ordenes_page.py

import logging
from typing import Any
from playwright.sync_api import Page, Response, TimeoutError as PlaywrightTimeoutError, Locator

from .sap_page_base import SAPPageBase
from data_models.zsin_ordenes_models import ZsinOrdenesFormData
from core.components.form.sap_form_component import SAPFormComponent
from core.components.form.sap_form_strategies import RangeFillStrategy

log = logging.getLogger(__name__)

class ZsinOrdenesPage(SAPPageBase):
    def __init__(self, page: Page, locator_provider: Any):
        super().__init__(page, locator_provider)

        # --- Componentes ---
        self.form = SAPFormComponent(self)

        # --- Locators del Formulario (se obtienen los strings del .toml) ---
        raw_form_locators = {
            'status': self._provider.get('form.status'),
            'mecanico': self._provider.get('form.mecanico'),
            'clase': self._provider.get('form.clase'),
            'cliente': self._provider.get('form.cliente'),
            'fechatope': self._provider.get('form.fechatope'),
            'fechainicio': self._provider.get('form.fechainicio'),
            'fechacreacion': self._provider.get('form.fechaicreacion')
        }
        
        # --- SOLUCIÓN: La página cumple su responsabilidad de crear los objetos Locator ---
        # Se convierte cada string de la lista en un objeto Locator de Playwright.
        self.form_locators: dict[str, list[Locator]] = {
            key: [self.playwright_page.locator(loc) for loc in loc_list]
            for key, loc_list in raw_form_locators.items()
        }

        # --- Locators de Resultados ---
        self.results_table = self.playwright_page.locator(self._provider.get('results.tabla'))
        self.select_all_button = self.playwright_page.locator(self._provider.get('results.seleccionar_todas'))
        self.toolbar_buttons = {
            'reenviar': self.playwright_page.locator(self._provider.get('results.toolbar.reenviar')),
            'imprimir': self.playwright_page.locator(self._provider.get('results.toolbar.imprimir'))
        }

        # --- Locators de Diálogo de Impresión ---
        self.print_dialog_button = self.playwright_page.locator(self._provider.get('print_dialog.boton_imprimir'))

    def rellenar_formulario(self, data: ZsinOrdenesFormData):
        """Rellena el formulario usando una estrategia para campos de rango."""
        strategy = RangeFillStrategy()
        self.form.fill_form(data, self.form_locators, strategy)

    def ejecutar_busqueda(self):
        """Ejecuta la búsqueda y espera a que la tabla de resultados esté visible."""
        log.info("Ejecutando la búsqueda en ZSIN_ORDENES...")
        self.execute()
        try:
            self.results_table.wait_for(timeout=20000)
            log.info("Búsqueda completada. Tabla de resultados visible.")
        except PlaywrightTimeoutError:
            log.warning("La tabla de resultados no apareció. Es posible que no haya resultados.")

    def hay_resultados(self) -> bool:
        """Comprueba si la tabla de resultados es visible."""
        return self.results_table.is_visible()

    def seleccionar_todas_las_ordenes(self):
        """Hace clic en el botón para seleccionar todas las filas de la tabla."""
        if self.select_all_button.is_visible():
            log.info("Seleccionando todas las órdenes...")
            self.select_all_button.click()
        else:
            log.warning("El botón para seleccionar todas las órdenes no está visible.")

    def reenviar_ordenes(self):
        """Hace clic en el botón de reenviar de la barra de herramientas."""
        log.info("Haciendo clic en 'Reenviar'...")
        self.toolbar_buttons['reenviar'].click()
        self.playwright_page.wait_for_timeout(5000) 

    def imprimir_ordenes_y_capturar_pdf(self, nombre_fichero_esperado: str) -> bytes:
        """Inicia el proceso de impresión y captura la respuesta de red que contiene el PDF."""
        log.info("Iniciando proceso de impresión y captura de PDF...")
        try:
            with self.playwright_page.expect_response(
                lambda response: nombre_fichero_esperado in response.url and "application/pdf" in response.headers.get("content-type", ""),
                timeout=90000
            ) as response_info:
                self.toolbar_buttons['imprimir'].click()
                self.print_dialog_button.wait_for()
                self.print_dialog_button.click()

            response = response_info.value
            if response.status != 200:
                raise ConnectionError(f"La descarga del PDF falló con status {response.status}")
            
            log.info("Respuesta de PDF capturada con éxito.")
            return response.body()
        except PlaywrightTimeoutError:
            log.error("Timeout esperando la respuesta del PDF. El proceso de impresión falló.")
            raise