# pages/sap_page_base.py

import logging
from .page_base import PageBase, Locator, PlaywrightTimeoutError # Deja Locator para que propague la importación a las que lo necesiten
from core.providers.locators.base_locator_provider import BaseLocatorProvider

log = logging.getLogger(__name__)

class SAPPageBase(PageBase):
    """
    Clase base especializada para páginas de SAP.
    Introduce la dependencia del locator_provider y define elementos/métodos comunes de SAP.
    """
    def __init__(self, page, locator_provider: BaseLocatorProvider):
        super().__init__(page)
        self._provider = locator_provider
        
        # Elementos comunes específicos de la UI de SAP
        self.status_bar = self.playwright_page.locator(self._provider.get('common.status_bar'))
        self.execute_button = self.playwright_page.locator(self._provider.get('common.ejecutar'))
        self.load_indicator = self.playwright_page.locator(self._provider.get('common.cargando'))

    # --- Métodos de Acción Específicos de SAP ---
    
    def get_status_bar_text(self) -> str:
        """Espera y devuelve el texto de la barra de estado de SAP."""
        self.status_bar.wait_for(state="visible")
        return self.status_bar.inner_text()

    def execute(self):
        """Hace clic en el botón 'Ejecutar' (F8) de SAP."""
        self.execute_button.click()

    # --- Método de espera robusto ---
    def _loading_disappear(self, timeout: int = 60000):
        """
        Espera a que el indicador de carga de SAP desaparezca.
        Esta es la forma más robusta de esperar a que una acción termine.
        """
        log.info("Esperando a que el indicador de carga desaparezca...")
        try:
            # Esperamos a que el elemento esté oculto o desasociado del DOM.
            self.load_indicator.wait_for(state="hidden", timeout=timeout)
            log.info("Indicador de carga ha desaparecido. La página está lista.")
        except PlaywrightTimeoutError:
            log.error("El indicador de carga no ha desaparecido en el tiempo esperado.")
            # Opcional: Podrías querer que el script falle aquí si la carga es infinita.
            raise