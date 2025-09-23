# Fichero: pages/sap_easy_access_page.py
# Descripción: Page Object para la pantalla SAP Easy Access.

import logging
from pages.sap_page_base import SAPPageBase
from core.providers.locators.base_locator_provider import BaseLocatorProvider

# Configuración del Logger
log = logging.getLogger(__name__)

class SAPEasyAccessPage(SAPPageBase):
    """
    Page Object para la pantalla SAP Easy Access.
    Hereda elementos y acciones comunes de SAPPageBase.
    """
    def __init__(self, page, locator_provider: BaseLocatorProvider):
        super().__init__(page, locator_provider)

        # Locators específicos de la pantalla SAP Easy Access
        self.transaction_input = self.page.locator(locator_provider.get('transaction_input'))
        self.ejecutar_button = self.page.locator(locator_provider.get('common.ejecutar'))
        self.continuar_button = self.page.locator(locator_provider.get('common.continuar'))

    def is_logged_in(self) -> bool:
        """
        Comprueba si la sesión está activa buscando un elemento único
        de esta página (como el campo de transacción).
        """
        try:
            self.transaction_input.wait_for(timeout=3000)
            log.debug("Campo de transacción encontrado: sesión activa.")
            return True
        except Exception as e:
            log.warning(f"Campo de transacción NO encontrado: sesión inactiva? Detalle: {e}")
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
        try:
            self.transaction_input.press("Enter")
            log.debug(f"Código de transacción ejecutado con ENTER.")
        except Exception as e:
            log.warning(f"Error al ejecutar la transacción pulsando ENTER, fallback con ejecutar: {e}")
            try:
                self.ejecutar_button.click()
            except Exception as e:
                log.warning(f"Error al ejecutar la transacción con el botón Ejecutar: {e} Último recurso, se continúa.")
                try:
                    self.continuar_button.click()  # En caso de que haya un botón "Continuar"
                except Exception as e:
                    log.error("No se ha podido ejecutar la transacción ni con ENTER, ni con Ejecutar, ni con Continuar." \
                    " Detalle: {e}")
                    raise