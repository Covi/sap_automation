# pages/sap_page_base.py

from .page_base import PageBase, Locator
from core.providers.locators.base_locator_provider import BaseLocatorProvider

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

    # --- Métodos de Acción Específicos de SAP ---
    
    def get_status_bar_text(self) -> str:
        """Espera y devuelve el texto de la barra de estado de SAP."""
        self.status_bar.wait_for(state="visible")
        return self.status_bar.inner_text()

    def execute(self):
        """Hace clic en el botón 'Ejecutar' (F8) de SAP."""
        self.execute_button.click()