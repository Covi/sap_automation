# services/transaction_service.py

import logging
from pages.sap_easy_access_page import SAPEasyAccessPage

log = logging.getLogger(__name__)


# services/transaction_service.py
import logging
from pages.sap_easy_access_page import SAPEasyAccessPage

log = logging.getLogger(__name__)

class TransactionService:
    """
    Servicio para la lógica de negocio de ejecutar una transacción de forma robusta.
    """
    def __init__(self, easy_access_page: SAPEasyAccessPage):
        self._easy_access_page = easy_access_page

    def run_transaction(self, transaction_code: str):
        """
        Ejecuta una transacción de forma robusta, asegurando que se
        termine cualquier sesión activa anterior mediante el prefijo '/n'.
        """
        # Combina /n con el código para crear un comando "absoluto".
        # Esto asegura que siempre funcione, sin importar desde dónde se llame.
        log.info(f"Iniciando transacción: {transaction_code}")
        self._easy_access_page.enter_transaction(f"/n{transaction_code}")
        self._easy_access_page.execute_transaction()

        # Esta espera es crucial para asegurar que la página de la transacción ha cargado
        # antes de que el script intente interactuar con ella.
        log.debug("Esperando a que el formulario de la nueva transacción esté visible...")
        self._easy_access_page.wait_for_transaction_form()