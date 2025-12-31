# services/transaction_service.py

import logging
from pages.sap_easy_access_page import SAPEasyAccessPage

log = logging.getLogger(__name__)

class TransactionService:
    def __init__(self, easy_access_page: SAPEasyAccessPage):
        self._easy_access_page = easy_access_page

    def run_transaction(self, command: str):
        """
        Ejecuta un comando en el cuadro de texto de SAP (Flujo Clásico).
        """
        log.info(f"Enviando comando clásico: {command}")
        self._easy_access_page.enter_transaction(command)
        self._easy_access_page.execute_transaction()
        self._easy_access_page.wait_for_transaction_form()