# services/transaction_service.py
# Servicio para ejecutar transacciones en SAP

from pages.sap_easy_access_page import SAPEasyAccessPage

class TransactionService:
    """
    Servicio para la lógica de negocio de ejecutar una transacción.
    """
    def __init__(self, easy_access_page: SAPEasyAccessPage):
        self._easy_access_page = easy_access_page

    def run_transaction(self, transaction_code: str):
        """
        Introduce un código de transacción y lo ejecuta.
        """
        self._easy_access_page.enter_transaction(transaction_code)
        self._easy_access_page.execute_transaction()

        self._easy_access_page.page.locator('form[ct="FOR"]') # FIXME hardcodeado