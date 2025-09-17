# Fichero: pages/sap_easy_access_page.py

import logging
from .sap_page_base import SAPPageBase
from .transaction_page import TransactionPage
from core.providers.locators.base_locator_provider import BaseLocatorProvider

log = logging.getLogger(__name__)

class SAPEasyAccessPage(SAPPageBase):
    """
    Representa la página inicial de SAP "Easy Access".
    Es el punto de entrada para lanzar transacciones.
    """
    def __init__(self, page, locator_provider: BaseLocatorProvider):
        super().__init__(page, locator_provider)
        # Locators específicos de esta página
        self._transaction_input = self.playwright_page.locator(self._provider.get('easy_access.transaction_input'))
        # Asumiendo que el botón de ejecutar en la barra de herramientas es el principal
        self._execute_button = self.playwright_page.locator(self._provider.get('common.ejecutar'))

    def enter_transaction(self, transaction_code: str):
        """
        Introduce un código de transacción en el campo de comandos.
        """
        log.info(f"Introduciendo código de transacción: {transaction_code}")
        self._transaction_input.fill(transaction_code)

    def execute_transaction(self) -> TransactionPage:
        """
        Ejecuta la transacción introducida (equivalente a pulsar Enter) y
        espera a que la siguiente página cargue.

        Devuelve:
            Una instancia de TransactionPage representando la pantalla de la transacción.
        """
        log.info("Ejecutando transacción...")
        # Usamos el método genérico de la clase base para pulsar Enter
        self.accept()
        
        # Se crea la instancia de la nueva página, pasándole el provider que ya tenemos.
        transaction_page = TransactionPage(self.playwright_page, self._provider)
        
        # El método de espera de la nueva página se encarga de confirmar la carga.
        # Devuelve la instancia de la página ya cargada para poder encadenar acciones.
        return transaction_page.wait_for_load()

    def click_execute_button(self):
        """
        Hace clic en el botón de ejecutar de la barra de herramientas (F8).
        Este es un método alternativo a pulsar Enter en el campo de transacción.
        """
        log.info("Haciendo clic en el botón de Ejecutar (F8)...")
        self._execute_button.click()