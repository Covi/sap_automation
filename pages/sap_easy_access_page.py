# Fichero: pages/sap_easy_access_page.py
# Descripción: Page Object para la pantalla SAP Easy Access.

from pages.sap_page_base import SAPPageBase
from core.providers.locators.base_locator_provider import BaseLocatorProvider

class SAPEasyAccessPage(SAPPageBase):
    """
    Page Object para la pantalla SAP Easy Access.
    Hereda elementos y acciones comunes de SAPPageBase.
    """
    def __init__(self, page, locator_provider: BaseLocatorProvider):
        super().__init__(page, locator_provider)
        # El único locator que esta página necesita
        self.transaction_input = self.playwright_page.locator(locator_provider.get('transaction_input'))

    def is_logged_in(self) -> bool:
        """
        Comprueba si la sesión está activa buscando un elemento único
        de esta página (como el campo de transacción).
        """
        # Asegúrate de que self.transaction_input es un locator que ya tienes definido
        # en el __init__ de esta clase.
        try:
            self.transaction_input.wait_for(timeout=3000)
            return True
        except Exception:
            return False

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
        # FIXME Como esto no funciona usamos el form self.page.wait_for_load_state("networkidle")
        self.form.wait_for()