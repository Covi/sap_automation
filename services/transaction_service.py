# Fichero: services/transaction_service.py

from pages.sap_easy_access_page import SAPEasyAccessPage
from pages.transaction_page import TransactionPage # <-- Importamos el tipo que se devuelve

class TransactionService:
    """
    Servicio para la lógica de negocio de ejecutar una transacción.
    """
    def __init__(self, easy_access_page: SAPEasyAccessPage):
        self._easy_access_page = easy_access_page

    def run_transaction(self, transaction_code: str) -> TransactionPage:
        """
        Introduce un código de transacción, lo ejecuta y devuelve la página resultante.
        """
        self._easy_access_page.enter_transaction(transaction_code)
        
        # Ahora el servicio solo orquesta, no conoce los detalles de la UI
        transaction_page = self._easy_access_page.execute_transaction()
        
        return transaction_page