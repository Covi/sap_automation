# Fichero: pages/sap_easy_access_page.py
# Descripción: Page Object para la pantalla SAP Easy Access.

from core.sap_page_base import SAPPageBase
from core.providers.base_provider import BaseLocatorProvider

class SAPEasyAccessPage(SAPPageBase):
    """
    Page Object para la pantalla SAP Easy Access.
    Hereda elementos y acciones comunes de SAPPageBase.
    """
    def __init__(self, page, locator_provider: BaseLocatorProvider):
        super().__init__(page, locator_provider)
        
        # El único locator que esta página necesita
        self.transaction_input = page.locator(locator_provider.get('transaction_input'))

    def enter_transaction(self, transaction_code: str):
        """
        Introduce un código de transacción en el campo correspondiente.
        """
        self.transaction_input.fill(transaction_code)

    def execute_transaction(self):
        """
        Lanza la transacción simulando la pulsación de la tecla 'Enter'
        en el campo de la transacción.
        """
        self.transaction_input.press("Enter")
        self.page.wait_for_load_state("networkidle")