# pages/sap_page_base.py

import logging
from .page_base import PageBase
# Importamos el handler concreto que necesitamos
from pages.handlers.playwright_handler import PlaywrightHandler 
# Importamos los tipos de Playwright que sí vamos a usar
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from core.providers.locators.base_locator_provider import BaseLocatorProvider

log = logging.getLogger(__name__)

class SAPPageBase(PageBase):
    """
    Clase base especializada para páginas de SAP.
    Depende de una implementación de Playwright para poder localizar elementos.
    """
    def __init__(self, handler: PlaywrightHandler, locator_provider: BaseLocatorProvider):
        # 1. Llamamos al constructor de la clase padre
        super().__init__(handler)
        
        # 2. Comprobación y "desempaquetado" del handler
        # Aunque el type hint ya pide PlaywrightHandler, esta es una validación en tiempo de ejecución.
        if not isinstance(self.handler, PlaywrightHandler):
            raise TypeError("SAPPageBase requiere un PlaywrightHandler para funcionar.")
        
        # Guardamos una referencia directa a la página de Playwright para uso interno.
        # La nombramos con un guion bajo para indicar que es para uso privado de esta clase.
        self._playwright_page: Page = self.handler.page

        # 3. El resto de la inicialización sigue igual, pero usando la referencia directa.
        self._provider = locator_provider
        
        self.status_bar: Locator = self._playwright_page.locator(self._provider.get('common.status_bar'))
        self.execute_button: Locator = self._playwright_page.locator(self._provider.get('common.ejecutar'))
        self.load_indicator: Locator = self._playwright_page.locator(self._provider.get('common.cargando'))

    # --- Métodos de Acción Específicos de SAP (no necesitan cambios) ---
    
    def get_status_bar_text(self) -> str:
        """Espera y devuelve el texto de la barra de estado de SAP."""
        self.status_bar.wait_for(state="visible")
        return self.status_bar.inner_text()

    def execute(self):
        """Hace clic en el botón 'Ejecutar' (F8) de SAP."""
        self.execute_button.click()

    # --- Método de espera robusto (no necesita cambios) ---
    def _loading_disappear(self, timeout: int = 60000):
        """Espera a que el indicador de carga de SAP desaparezca."""
        log.info("Esperando a que el indicador de carga desaparezca...")
        try:
            self.load_indicator.wait_for(state="hidden", timeout=timeout)
            log.info("Indicador de carga ha desaparecido. La página está lista.")
        except PlaywrightTimeoutError:
            log.error("El indicador de carga no ha desaparecido en el tiempo esperado.")
            raise